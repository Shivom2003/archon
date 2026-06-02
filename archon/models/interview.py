"""Models for the Phase 2 LLM-driven interview session and its captured data."""

from pydantic import BaseModel, Field

from archon.models.enums import ComplianceRequirement, Priority


class TechStack(BaseModel):
    """Technology choices captured during Phase 2."""

    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    infra_cloud: list[str] = Field(default_factory=list, description="Cloud/infra providers")
    other: list[str] = Field(default_factory=list, description="Any other notable tools")

    def is_empty(self) -> bool:
        return not any([
            self.languages, self.frameworks, self.databases,
            self.infra_cloud, self.other,
        ])


class ProjectConstraints(BaseModel):
    """Constraints and non-functional requirements captured during Phase 2."""

    compliance: list[ComplianceRequirement] = Field(default_factory=list)
    existing_codebase: bool = Field(
        default=False,
        description="Whether the project is being added to an existing codebase",
    )
    existing_stack_notes: str = Field(
        default="",
        description="Notes about the existing stack if existing_codebase=True",
    )
    budget_range: str = Field(default="", description="e.g. 'bootstrapped', '$500/mo infra'")
    timeline: str = Field(default="", description="e.g. '3 months MVP', '2 weeks prototype'")
    key_constraints: list[str] = Field(
        default_factory=list,
        description="Hard constraints (e.g. 'must use AWS', 'no vendor lock-in')",
    )


class CoreFeature(BaseModel):
    """A single core feature of the project."""

    name: str
    description: str
    priority: Priority = Priority.MUST_HAVE


class InterviewTurn(BaseModel):
    """A single turn in the Phase 2 LLM conversation."""

    role: str  # "assistant" | "user"
    content: str


class Phase2Data(BaseModel):
    """
    All structured data captured by Claude's tool calls during Phase 2.
    Built up incrementally as Claude calls record_* tools.
    """

    tech_stack: TechStack = Field(default_factory=TechStack)
    constraints: ProjectConstraints = Field(default_factory=ProjectConstraints)
    core_features: list[CoreFeature] = Field(default_factory=list)
    magic_moment: str = Field(
        default="",
        description="The single most important user experience to optimise for",
    )
    interview_summary: str = Field(
        default="",
        description="Claude's synthesis summary at the end of the interview",
    )
    conversation_history: list[InterviewTurn] = Field(
        default_factory=list,
        description="Full conversation log for debugging / reproducibility",
    )

    def add_turn(self, role: str, content: str) -> None:
        self.conversation_history.append(InterviewTurn(role=role, content=content))
