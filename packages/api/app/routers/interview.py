"""
Interview router — Phase 1, Phase 2 SSE, synthesis, spec retrieval, download.
"""

import io
import json
import uuid
import zipfile
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from archon.models.interview import Phase2Data
from archon.models.project import ProjectConfig
from archon.models.spec import ArchitectSpec
from archon.generators import all_generators
from app.auth import require_beta_access
from app.database import get_db
from app.models import Project
from app.schemas import InterviewMessage, Phase1Submit, ProjectDetail, SpecFileResponse
from app.services.interview_svc import run_phase2_turn, validate_phase1
from app.services.synthesis_svc import run_synthesis

router = APIRouter()

# Valid rendered spec filenames
SPEC_FILES = {"SPEC.md", "ARCHITECTURE.md", "ROADMAP.md", "DECISIONS.md", "AGENTS.md", "CLAUDE.md"}


# ── Phase 1 ───────────────────────────────────────────────────────────────────


@router.patch("/{project_id}/phase1", response_model=ProjectDetail)
async def submit_phase1(
    project_id: uuid.UUID,
    body: Phase1Submit,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Submit Phase 1 form data. Validates and stores ProjectConfig, moves state → phase2."""
    project = await _get_owned(project_id, user_id, db)

    if project.state not in ("phase1",):
        raise HTTPException(409, f"Cannot submit Phase 1 from state '{project.state}'")

    try:
        config = validate_phase1(body)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    project.phase1_data = config.model_dump(mode="json")
    # Initialise empty Phase2Data
    project.phase2_data = Phase2Data().model_dump(mode="json")
    project.state = "phase2"
    project.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(project)
    return project


# ── Phase 2 SSE ───────────────────────────────────────────────────────────────


@router.get("/{project_id}/interview/stream")
async def stream_interview(
    project_id: uuid.UUID,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    SSE endpoint for the first Phase 2 turn (Claude asks the opening question).
    The frontend connects here immediately after Phase 1 to kick off the interview.
    """
    project = await _get_owned(project_id, user_id, db)
    if project.state != "phase2":
        raise HTTPException(409, f"Project not in phase2 (state: {project.state})")

    config = ProjectConfig.model_validate(project.phase1_data)
    phase2 = Phase2Data.model_validate(project.phase2_data)
    messages: list[dict] = _rebuild_messages(phase2)

    # Kick-off message for the very first turn
    kick_off = "I've completed the intake form. Please start by asking about my tech stack."
    messages_state = messages  # mutable reference

    async def generate():
        async for event in run_phase2_turn(config, phase2, messages_state, kick_off):
            yield event
        # Persist updated phase2 state
        project.phase2_data = phase2.model_dump(mode="json")
        project.updated_at = datetime.now(UTC)
        await db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/{project_id}/interview/message")
async def send_message(
    project_id: uuid.UUID,
    body: InterviewMessage,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Send a user message during Phase 2 and stream Claude's response.
    Each call is one complete turn (user speaks → Claude responds).
    """
    project = await _get_owned(project_id, user_id, db)
    if project.state != "phase2":
        raise HTTPException(409, f"Project not in phase2 (state: {project.state})")

    config = ProjectConfig.model_validate(project.phase1_data)
    phase2 = Phase2Data.model_validate(project.phase2_data)
    messages: list[dict] = _rebuild_messages(phase2)

    async def generate():
        async for event in run_phase2_turn(config, phase2, messages, body.content):
            yield event
        project.phase2_data = phase2.model_dump(mode="json")
        project.updated_at = datetime.now(UTC)
        await db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── Synthesis ─────────────────────────────────────────────────────────────────


@router.post("/{project_id}/synthesize", status_code=202)
async def trigger_synthesis(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Trigger the architecture synthesis pass as a background task.
    Client should poll GET /projects/{id} until state == 'complete' or 'failed'.
    """
    project = await _get_owned(project_id, user_id, db)
    if project.state not in ("phase2",):
        raise HTTPException(409, f"Cannot synthesize from state '{project.state}'")
    if not project.phase2_data:
        raise HTTPException(400, "Phase 2 not yet completed")

    background_tasks.add_task(run_synthesis, project, db)
    return {"message": "Synthesis started", "project_id": str(project_id)}


# ── Spec retrieval ────────────────────────────────────────────────────────────


@router.get("/{project_id}/spec")
async def get_spec(
    project_id: uuid.UUID,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return the full ArchitectSpec as JSON."""
    project = await _get_owned(project_id, user_id, db)
    _require_complete(project)
    return project.spec_data  # type: ignore[return-value]


@router.get("/{project_id}/spec/{filename}", response_model=SpecFileResponse)
async def get_spec_file(
    project_id: uuid.UUID,
    filename: str,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> SpecFileResponse:
    """Return a single rendered .md file from the spec."""
    if filename not in SPEC_FILES:
        raise HTTPException(404, f"Unknown spec file '{filename}'. Valid: {sorted(SPEC_FILES)}")

    project = await _get_owned(project_id, user_id, db)
    _require_complete(project)

    spec = ArchitectSpec.model_validate(project.spec_data)
    content = _render_spec_file(spec, filename)
    return SpecFileResponse(filename=filename, content=content)


@router.get("/{project_id}/download")
async def download_spec(
    project_id: uuid.UUID,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download the complete .architect/ directory as a zip archive."""
    project = await _get_owned(project_id, user_id, db)
    _require_complete(project)

    spec = ArchitectSpec.model_validate(project.spec_data)
    zip_bytes = _build_zip(spec)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{project.name}-architect.zip"'},
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _get_owned(project_id: uuid.UUID, user_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(404, "Project not found")
    if project.clerk_user_id != user_id:
        raise HTTPException(403, "Not your project")
    return project


def _require_complete(project: Project) -> None:
    if project.state != "complete" or not project.spec_data:
        raise HTTPException(409, f"Spec not ready (state: {project.state})")


def _rebuild_messages(phase2: Phase2Data) -> list[dict]:
    """Reconstruct the LLM messages list from the conversation history."""
    return [{"role": t.role, "content": t.content} for t in phase2.conversation_history]


def _render_spec_file(spec: ArchitectSpec, filename: str) -> str:
    """Render a single spec file using the appropriate generator."""
    from archon.generators import (
        AgentsMdGenerator, ArchitectureGenerator, ClaudeMdGenerator,
        DecisionsGenerator, RoadmapGenerator, SpecGenerator,
    )
    gen_map = {
        "SPEC.md": SpecGenerator,
        "ARCHITECTURE.md": ArchitectureGenerator,
        "ROADMAP.md": RoadmapGenerator,
        "DECISIONS.md": DecisionsGenerator,
        "AGENTS.md": AgentsMdGenerator,
        "CLAUDE.md": ClaudeMdGenerator,
    }
    return gen_map[filename](spec).render()


def _build_zip(spec: ArchitectSpec) -> bytes:
    """Build an in-memory zip of all .architect/ files."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for gen in all_generators(spec):
            zf.writestr(f".architect/{gen.output_filename}", gen.render())
        # Include the raw spec JSON
        zf.writestr(".architect/spec.json", spec.to_json())
    return buf.getvalue()
