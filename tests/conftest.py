"""Shared pytest fixtures."""

from pathlib import Path

import pytest

from archon.models.enums import (
    AgenticTool,
    ConsumerScale,
    DevScale,
    ExpertiseLevel,
    ProjectType,
    SubscriptionTier,
)
from archon.models.interview import CoreFeature, Phase2Data, ProjectConstraints, TechStack
from archon.models.project import ProjectConfig, ToolSubscription

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config() -> ProjectConfig:
    return ProjectConfig(
        name="taskflow",
        description="A lightweight task management API for small teams",
        project_type=ProjectType.API_SERVICE,
        consumer_scale=ConsumerScale.SMALL_TEAM,
        dev_scale=DevScale.SOLO,
        agentic_tools=[AgenticTool.CLAUDE_CODE],
        distribute_across_agents=False,
        tool_subscriptions=[ToolSubscription(tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.PRO)],
        expertise_level=ExpertiseLevel.INTERMEDIATE,
    )


@pytest.fixture
def sample_phase2() -> Phase2Data:
    from archon.models.enums import Priority

    return Phase2Data(
        tech_stack=TechStack(
            languages=["Python"],
            frameworks=["FastAPI", "SQLAlchemy"],
            databases=["PostgreSQL", "Redis"],
            infra_cloud=["Railway"],
            other=["Stripe"],
        ),
        constraints=ProjectConstraints(
            existing_codebase=False,
            budget_range="bootstrapped",
            timeline="6-week MVP",
            key_constraints=["must be open source"],
        ),
        core_features=[
            CoreFeature(name="Task CRUD", description="Create/read/update/delete tasks", priority=Priority.MUST_HAVE),
            CoreFeature(
                name="Team workspaces",
                description="Isolated workspaces per team",
                priority=Priority.MUST_HAVE,
            ),
            CoreFeature(name="Activity feed", description="Real-time feed of changes", priority=Priority.SHOULD_HAVE),
        ],
        magic_moment="The moment a developer calls POST /tasks and gets an immediately usable response",
        interview_summary="A clean REST API for team task management built with FastAPI.",
    )


@pytest.fixture
def sample_spec(sample_config, sample_phase2):
    """A minimal but valid ArchitectSpec for testing generators."""
    from archon.models.spec import (
        ApiEndpoint,
        ArchitectSpec,
        ArchitectureData,
        ArchitectureDecision,
        Checkpoint,
        DataEntity,
        RoadmapData,
        RoadmapPhase,
        RoadmapTask,
        SystemComponent,
    )

    return ArchitectSpec(
        project=sample_config,
        phase2=sample_phase2,
        architecture=ArchitectureData(
            tech_stack=sample_phase2.tech_stack,
            architecture_style="Monolith",
            deployment_strategy="Single Railway service with PostgreSQL add-on",
            components=[
                SystemComponent(
                    name="API Server",
                    description="FastAPI application serving REST endpoints",
                    technology="FastAPI",
                    responsibilities=["Request routing", "Auth validation", "Business logic"],
                    communicates_with=["Database", "Cache"],
                ),
                SystemComponent(
                    name="Database",
                    description="Primary data store",
                    technology="PostgreSQL",
                    responsibilities=["Persistent storage", "ACID transactions"],
                    communicates_with=[],
                ),
            ],
            data_entities=[
                DataEntity(
                    name="Task",
                    description="A unit of work assigned to a team member",
                    key_fields=["id", "title", "status", "assignee_id", "workspace_id", "due_date"],
                    relationships=["belongs to Workspace", "assigned to User"],
                ),
            ],
            api_endpoints=[
                ApiEndpoint(method="POST", path="/tasks", description="Create a new task"),
                ApiEndpoint(method="GET", path="/tasks/{id}", description="Fetch a task by ID"),
            ],
            security_notes=["JWT authentication on all routes", "Workspace isolation enforced at DB level"],
            scalability_notes=["Redis for session caching", "DB connection pooling via asyncpg"],
        ),
        roadmap=RoadmapData(
            phases=[
                RoadmapPhase(
                    number=1,
                    name="Foundation",
                    description="Project scaffold and database setup",
                    primary_agent=AgenticTool.CLAUDE_CODE,
                    agent_rationale="Claude Code excels at setting up project structure and writing migrations",
                    tasks=[
                        RoadmapTask(title="Initialise FastAPI project", estimated_turns=2),
                        RoadmapTask(title="Set up SQLAlchemy models", estimated_turns=3),
                        RoadmapTask(title="Write Alembic migrations", estimated_turns=2),
                    ],
                    estimated_turns_total=7,
                    success_criteria=["All migrations pass", "FastAPI app starts"],
                    checkpoint=Checkpoint(
                        after_task="Write Alembic migrations",
                        turns_used_estimate=7,
                        reason="Good stopping point before beginning API layer.",
                        resume_prompt=(
                            "Continue taskflow project. Phase 1 complete "
                            "(DB schema + migrations passing). Begin Phase 2: "
                            "API Layer. Context: .architect/ARCHITECTURE.md"
                        ),
                    ),
                ),
            ],
            core_features=sample_phase2.core_features,
        ),
        decisions=[
            ArchitectureDecision(
                number=1,
                title="Monolith over microservices",
                status="accepted",
                context="Solo developer building a 6-week MVP on a bootstrapped budget.",
                decision="Use a single FastAPI monolith rather than microservices.",
                rationale="Microservices add operational complexity that outweighs benefits at this scale.",
                trade_offs=["Harder to extract services later", "Single point of failure"],
                alternatives_considered=["FastAPI microservices", "Django monolith"],
            ),
        ],
    )
