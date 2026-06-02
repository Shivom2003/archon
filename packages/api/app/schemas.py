"""Pydantic request/response DTOs for all API endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Projects ─────────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)


class ProjectSummary(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    state: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectSummary):
    phase1_data: dict | None = None
    phase2_data: dict | None = None
    spec_data: dict | None = None
    error: str = ""


# ── Phase 1 ───────────────────────────────────────────────────────────────────


class Phase1Submit(BaseModel):
    """Mirrors archon.models.project.ProjectConfig — validated server-side."""

    name: str
    description: str
    project_type: str
    consumer_scale: str
    dev_scale: str
    agentic_tools: list[str] = Field(min_length=1)
    distribute_across_agents: bool = False
    tool_subscriptions: list[dict] = Field(default_factory=list)
    expertise_level: str


# ── Phase 2 ───────────────────────────────────────────────────────────────────


class InterviewMessage(BaseModel):
    """User message sent during Phase 2."""

    content: str = Field(min_length=1, max_length=4000)


# ── Spec ──────────────────────────────────────────────────────────────────────


class SpecFileResponse(BaseModel):
    filename: str
    content: str
    content_type: str = "text/markdown"


# ── Generic ───────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    detail: str
