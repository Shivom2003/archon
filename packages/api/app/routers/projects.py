"""Project CRUD endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_beta_access
from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectDetail, ProjectSummary

router = APIRouter()


@router.get("", response_model=list[ProjectSummary])
async def list_projects(
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> list[Project]:
    """List all projects belonging to the current user, newest first."""
    result = await db.execute(
        select(Project)
        .where(Project.clerk_user_id == user_id)
        .order_by(Project.updated_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=ProjectSummary, status_code=201)
async def create_project(
    body: ProjectCreate,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Create a new project (starts in state='phase1')."""
    project = Project(
        clerk_user_id=user_id,
        name=body.name,
        description=body.description,
    )
    db.add(project)
    await db.flush()
    return project


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Get full project details including spec data if complete."""
    return await _get_owned_project(project_id, user_id, db)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    user_id: str = Depends(require_beta_access),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a project."""
    project = await _get_owned_project(project_id, user_id, db)
    await db.delete(project)


# ── Shared helper ─────────────────────────────────────────────────────────────


async def _get_owned_project(
    project_id: uuid.UUID,
    user_id: str,
    db: AsyncSession,
) -> Project:
    """Fetch a project, enforcing ownership. Raises 404 or 403."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(404, "Project not found")
    if project.clerk_user_id != user_id:
        raise HTTPException(403, "Not your project")
    return project
