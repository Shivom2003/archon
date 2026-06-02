"""
ArchitectSpec — the root output model.
Every generator reads from this single source of truth.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from archon.models.enums import AgenticTool, Priority, RoadmapPhaseStatus
from archon.models.interview import CoreFeature, Phase2Data, ProjectConstraints, TechStack
from archon.models.project import ProjectConfig


# ---------------------------------------------------------------------------
# Architecture sub-models
# ---------------------------------------------------------------------------


class SystemComponent(BaseModel):
    """A logical component of the system (e.g. API server, database, cache)."""

    name: str
    description: str
    technology: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    communicates_with: list[str] = Field(default_factory=list, description="Component names")


class ApiEndpoint(BaseModel):
    """A high-level API endpoint or RPC."""

    method: str = ""          # GET, POST, etc. (empty for non-HTTP)
    path: str
    description: str
    request_shape: str = ""   # brief human-readable description
    response_shape: str = ""


class DataEntity(BaseModel):
    """A core data entity / domain model."""

    name: str
    description: str
    key_fields: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)


class ArchitectureData(BaseModel):
    """Full technical architecture."""

    tech_stack: TechStack
    components: list[SystemComponent] = Field(default_factory=list)
    data_entities: list[DataEntity] = Field(default_factory=list)
    api_endpoints: list[ApiEndpoint] = Field(default_factory=list)
    architecture_style: str = Field(
        default="",
        description="e.g. 'monolith', 'microservices', 'serverless', 'event-driven'",
    )
    deployment_strategy: str = Field(default="")
    security_notes: list[str] = Field(default_factory=list)
    scalability_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Roadmap sub-models
# ---------------------------------------------------------------------------


class RoadmapTask(BaseModel):
    """An individual task within a roadmap phase."""

    title: str
    description: str = ""
    estimated_turns: int = Field(default=1, description="Estimated agent turns to complete")


class Checkpoint(BaseModel):
    """A suggested pause point for agents respecting usage limits."""

    after_task: str = Field(description="Task title after which to checkpoint")
    turns_used_estimate: int
    reason: str
    resume_prompt: str = Field(
        description="Exact prompt the user can paste to resume in a new session"
    )


class RoadmapPhase(BaseModel):
    """A development phase with task breakdown and agent assignment."""

    number: int
    name: str
    description: str = ""
    primary_agent: AgenticTool
    agent_rationale: str = Field(
        default="", description="Why this agent is best for this phase"
    )
    tasks: list[RoadmapTask] = Field(default_factory=list)
    estimated_turns_total: int = 0
    checkpoint: Checkpoint | None = None
    status: RoadmapPhaseStatus = RoadmapPhaseStatus.PENDING
    success_criteria: list[str] = Field(default_factory=list)


class RoadmapData(BaseModel):
    """Complete development roadmap."""

    phases: list[RoadmapPhase] = Field(default_factory=list)
    core_features: list[CoreFeature] = Field(default_factory=list)

    @property
    def total_estimated_turns(self) -> int:
        return sum(p.estimated_turns_total for p in self.phases)


# ---------------------------------------------------------------------------
# Architecture Decision Records
# ---------------------------------------------------------------------------


class ArchitectureDecision(BaseModel):
    """An Architecture Decision Record (ADR)."""

    number: int
    title: str
    status: str = "accepted"        # accepted | proposed | deprecated | superseded
    context: str = Field(description="What situation prompted this decision?")
    decision: str = Field(description="What was decided?")
    rationale: str = Field(description="Why was this the right choice?")
    trade_offs: list[str] = Field(default_factory=list)
    alternatives_considered: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class ArchitectSpec(BaseModel):
    """
    The complete architecture specification for a project.
    This is the canonical data model — all generators render from this.

    Schema version is semver-minor bumped when new required fields are added.
    Generators must handle older versions gracefully.
    """

    schema_version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    project: ProjectConfig
    phase2: Phase2Data
    architecture: ArchitectureData
    roadmap: RoadmapData
    decisions: list[ArchitectureDecision] = Field(default_factory=list)

    # Convenience accessors
    @property
    def constraints(self) -> ProjectConstraints:
        return self.phase2.constraints

    @property
    def features(self) -> list[CoreFeature]:
        return self.phase2.core_features

    @property
    def must_have_features(self) -> list[CoreFeature]:
        return [f for f in self.features if f.priority == Priority.MUST_HAVE]

    def to_json(self, **kwargs) -> str:
        """Serialize to JSON string (for saving .architect/spec.json)."""
        return self.model_dump_json(indent=2, **kwargs)

    @classmethod
    def from_json(cls, data: str) -> "ArchitectSpec":
        """Deserialize from JSON string."""
        return cls.model_validate_json(data)
