"""
Prompts for the Phase 2 LLM-driven interview.

The system prompt is injected with Phase 1 data and tells Claude to act
as a senior technical architect interviewing the developer. Claude uses
structured tool calls to capture data — never free-form text.
"""

from archon.models.project import ProjectConfig


def build_phase2_system_prompt(config: ProjectConfig) -> str:
    """
    Build the system prompt for Phase 2, injecting Phase 1 structured data.
    This prompt is cached — it's sent once and reused across all turns.
    """
    tools_str = ", ".join(t.label for t in config.agentic_tools)
    return f"""You are a senior software architect helping a developer plan their project. \
Your job is to ask targeted follow-up questions and use the provided tools to capture \
structured information about their project.

## Project Context (from initial intake)

- **Name:** {config.name}
- **Description:** {config.description}
- **Type:** {config.project_type.label}
- **Consumer Scale:** {config.consumer_scale.label}
- **Dev Scale:** {config.dev_scale.label}
- **Agentic Tools:** {tools_str}
- **Multi-agent distribution:** {"Yes" if config.distribute_across_agents else "No"}
- **Expertise Level:** {config.expertise_level.label}

## Your Behaviour

1. Ask ONE focused question per turn — do not overwhelm the user with a list.
2. Adapt your questions based on their expertise level:
   - Novice: suggest options, explain trade-offs briefly
   - Intermediate: offer guidance but respect their choices
   - Expert: be direct, skip obvious recommendations
3. Use the `record_tech_stack` tool whenever you've gathered enough info about \
technologies — you can call it multiple times to add more.
4. Use `record_constraints` when you understand their compliance, budget, \
timeline, or hard constraints.
5. Use `record_core_feature` for each important feature you discover — aim for \
3–7 features maximum.
6. Use `record_magic_moment` once you understand the single most important \
user experience they're optimising for.
7. Once you have covered tech stack, constraints, and at least 3 features, \
call `complete_interview` with a concise synthesis summary.
8. Do NOT ask about things already captured in the Project Context above.
9. Keep your conversational messages brief and friendly — under 100 words per turn.
10. If the user is a novice and hasn't mentioned a tech stack at all, \
suggest a sensible default based on the project type and ask for confirmation \
before recording it.

## Tone

Professional but conversational. You are a technical peer, not a form wizard. \
Ask follow-up questions naturally ("And what about authentication — are you \
thinking OAuth, or rolling your own?").
"""


# Tool definitions passed to Claude during Phase 2
PHASE2_TOOLS: list[dict] = [
    {
        "name": "record_tech_stack",
        "description": (
            "Record the technology choices for the project. "
            "Can be called multiple times to add more information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Programming languages (e.g. ['Python', 'TypeScript'])",
                },
                "frameworks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Frameworks and libraries (e.g. ['FastAPI', 'React', 'Next.js'])",
                },
                "databases": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Databases and data stores (e.g. ['PostgreSQL', 'Redis'])",
                },
                "infra_cloud": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Infrastructure and cloud providers (e.g. ['AWS', 'Vercel', 'Docker'])",
                },
                "other": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Other notable tools (e.g. ['Stripe', 'SendGrid', 'Sentry'])",
                },
            },
            "required": [],
        },
    },
    {
        "name": "record_constraints",
        "description": "Record project constraints and non-functional requirements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "compliance": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["none", "gdpr", "hipaa", "soc2", "pci_dss", "iso_27001", "ccpa", "other"],
                    },
                    "description": "Regulatory/compliance requirements",
                },
                "existing_codebase": {
                    "type": "boolean",
                    "description": "Is this being added to an existing codebase?",
                },
                "existing_stack_notes": {
                    "type": "string",
                    "description": "Notes about existing stack if applicable",
                },
                "budget_range": {
                    "type": "string",
                    "description": "e.g. 'bootstrapped', '$500/mo infra budget', 'enterprise budget'",
                },
                "timeline": {
                    "type": "string",
                    "description": "e.g. '3-month MVP', '2-week prototype', 'no deadline'",
                },
                "key_constraints": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Hard constraints (e.g. 'must use AWS', 'no vendor lock-in', 'open source only')",
                },
            },
            "required": [],
        },
    },
    {
        "name": "record_core_feature",
        "description": "Record a single core feature of the project. Call once per feature.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Short feature name (e.g. 'User authentication')",
                },
                "description": {
                    "type": "string",
                    "description": "What this feature does and why it matters",
                },
                "priority": {
                    "type": "string",
                    "enum": ["must_have", "should_have", "nice_to_have", "future"],
                    "description": "Feature priority",
                },
            },
            "required": ["name", "description", "priority"],
        },
    },
    {
        "name": "record_magic_moment",
        "description": (
            "Record the single most important user experience the project is optimising for. "
            "Call this once when you understand the project's core value proposition."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "magic_moment": {
                    "type": "string",
                    "description": (
                        "One sentence describing the 'aha' moment "
                        "(e.g. 'The moment a user pastes their project description and sees "
                        "a complete architecture spec in 30 seconds')"
                    ),
                },
            },
            "required": ["magic_moment"],
        },
    },
    {
        "name": "complete_interview",
        "description": (
            "Signal that the interview is complete. Call this when you have gathered "
            "sufficient information about the tech stack, constraints, and core features. "
            "Provide a concise synthesis summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": (
                        "2–4 sentence synthesis of the project: what it is, "
                        "key technical decisions made, and the main challenge to solve."
                    ),
                },
            },
            "required": ["summary"],
        },
    },
]
