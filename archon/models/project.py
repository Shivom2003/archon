"""ProjectConfig — captures all structured data from the Phase 1 interview."""

from pydantic import BaseModel, Field

from archon.models.enums import (
    AgenticTool,
    ConsumerScale,
    DevScale,
    ExpertiseLevel,
    ProjectType,
    SubscriptionTier,
)


class ToolSubscription(BaseModel):
    """A user's subscription to a specific agentic tool."""

    tool: AgenticTool
    tier: SubscriptionTier

    def __str__(self) -> str:
        return f"{self.tool.label} ({self.tier.label})"


class ProjectConfig(BaseModel):
    """
    All structured data captured during the Phase 1 interview.
    This is the seed for the Phase 2 LLM conversation.
    """

    # Q1 — Identity
    name: str = Field(description="Short project name (used as a directory/package name)")
    description: str = Field(description="One-sentence description of what the project does")

    # Q2 — Project type
    project_type: ProjectType = Field(description="Primary category of the project")

    # Q3 — Consumer scale
    consumer_scale: ConsumerScale = Field(description="Expected scale from the end-user / consumer perspective")

    # Q4 — Dev scale
    dev_scale: DevScale = Field(description="Scale from the development team perspective")

    # Q5 — Agentic tools
    agentic_tools: list[AgenticTool] = Field(
        description="Agentic coding tools the developer will use",
        min_length=1,
    )

    # Q6 — Multi-agent distribution
    distribute_across_agents: bool = Field(
        default=False,
        description=(
            "Whether to distribute tasks across multiple agents in the roadmap. "
            "Only meaningful when >1 tool is selected."
        ),
    )

    # Q7 — Subscription tiers (one per selected tool)
    tool_subscriptions: list[ToolSubscription] = Field(
        default_factory=list,
        description="Subscription tier for each selected agentic tool",
    )

    # Q8 — Expertise
    expertise_level: ExpertiseLevel = Field(description="Developer's self-assessed expertise level")

    def get_subscription(self, tool: AgenticTool) -> SubscriptionTier | None:
        """Return the subscription tier for a given tool, or None if not configured."""
        for sub in self.tool_subscriptions:
            if sub.tool == tool:
                return sub.tier
        return None

    @property
    def primary_tool(self) -> AgenticTool:
        """The first (primary) agentic tool selected."""
        return self.agentic_tools[0]
