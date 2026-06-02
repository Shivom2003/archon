"""
Synthesis service — runs the architecture generation pass asynchronously
and updates the project row in the database.
"""

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

from archon.llm.registry import get_client
from archon.models.interview import Phase2Data
from archon.models.project import ProjectConfig
from archon.synthesizer import synthesize
from app.models import Project

logger = logging.getLogger(__name__)


async def run_synthesis(project: Project, db: AsyncSession) -> None:
    """
    Run the synthesis pass for a project.
    Updates project.state and project.spec_data in the DB.
    Called as a background task from the synthesize endpoint.
    """
    if not project.phase1_data or not project.phase2_data:
        logger.error("Project %s missing phase data for synthesis", project.id)
        project.state = "failed"
        project.error = "Missing phase data"
        await db.commit()
        return

    project.state = "synthesizing"
    await db.commit()

    try:
        config = ProjectConfig.model_validate(project.phase1_data)
        phase2 = Phase2Data.model_validate(project.phase2_data)

        synthesis_model = os.getenv("ARCHON_SYNTHESIS_MODEL", "claude-sonnet-4-5")
        llm = get_client(synthesis_model)

        spec = await synthesize(config, phase2, llm)

        project.spec_data = spec.model_dump(mode="json")
        project.state = "complete"
        project.error = ""
        logger.info("Synthesis complete for project %s", project.id)

    except Exception as exc:
        logger.exception("Synthesis failed for project %s", project.id)
        project.state = "failed"
        project.error = str(exc)

    await db.commit()
