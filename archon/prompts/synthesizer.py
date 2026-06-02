"""
Prompts for the architecture synthesis pass.

After the interview completes, a separate Claude call synthesises all gathered
data into a structured ArchitectSpec. This uses extended thinking when available
for deeper architectural reasoning.
"""

from archon.models.interview import Phase2Data
from archon.models.project import ProjectConfig
from archon.models.spec import ArchitectSpec


def build_synthesis_system_prompt() -> str:
    """
    System prompt for the architecture synthesis call.
    Cached — large and static across all synthesis requests.
    """
    return """You are a senior software architect generating a comprehensive project \
architecture specification. You will receive a complete project profile gathered during \
an interview and must produce a detailed, structured architecture document.

## Output Requirements

You MUST call the `generate_architecture_spec` tool with ALL fields populated. \
This is not optional — your entire response must be the tool call.

## Architecture Principles

1. **Justify every decision** — every tech choice must have a rationale.
2. **Be specific** — no vague advice like "use a caching layer"; say "Redis for \
session caching with a 24-hour TTL".
3. **Match scale** — a solo developer's personal project and an enterprise SaaS have \
very different architectures. Don't over-engineer or under-engineer.
4. **Agent-friendly output** — descriptions should be precise enough that an AI agent \
can implement them without ambiguity.
5. **Roadmap realism** — task turn estimates should reflect real agentic coding \
sessions. A "set up FastAPI project with Pydantic models" is ~3–5 turns, not 1.
6. **Checkpoint honesty** — if a user has a limited subscription plan, insert \
checkpoints at natural stopping points, with accurate resume prompts.
7. **ADRs over assumptions** — if there was a meaningful architectural fork in the \
road (monolith vs. microservices, SQL vs. NoSQL), capture it as a decision record.

## Constraints

- Generate 3–6 roadmap phases for most projects (more for complex, fewer for simple)
- Generate 3–7 ADRs for most projects
- Each roadmap phase should have 3–8 tasks
- Component names must be consistent across all sections
- Resume prompts in checkpoints must be copy-pasteable and self-contained
"""


def build_synthesis_user_prompt(config: ProjectConfig, phase2: Phase2Data) -> str:
    """Build the user-turn prompt for the synthesis call."""
    features_str = "\n".join(
        f"- [{f.priority.value.upper()}] {f.name}: {f.description}"
        for f in phase2.core_features
    ) or "  (none captured)"

    compliance_str = ", ".join(c.value for c in phase2.constraints.compliance) or "none"
    constraints_str = "\n".join(
        f"- {c}" for c in phase2.constraints.key_constraints
    ) or "  (none)"

    tools_str = "\n".join(
        f"- {t.label} ({config.get_subscription(t) or 'unknown tier'})"
        for t in config.agentic_tools
    )

    return f"""## Project Profile

**Name:** {config.name}
**Description:** {config.description}
**Type:** {config.project_type.label}
**Consumer Scale:** {config.consumer_scale.label}
**Dev Scale:** {config.dev_scale.label}
**Developer Expertise:** {config.expertise_level.label}
**Multi-agent distribution:** {"Yes" if config.distribute_across_agents else "No"}

## Agentic Tools
{tools_str}

## Tech Stack
- Languages: {", ".join(phase2.tech_stack.languages) or "not specified"}
- Frameworks: {", ".join(phase2.tech_stack.frameworks) or "not specified"}
- Databases: {", ".join(phase2.tech_stack.databases) or "not specified"}
- Infrastructure: {", ".join(phase2.tech_stack.infra_cloud) or "not specified"}
- Other: {", ".join(phase2.tech_stack.other) or "not specified"}

## Core Features
{features_str}

## Magic Moment
{phase2.magic_moment or "Not captured"}

## Constraints
- Compliance: {compliance_str}
- Existing codebase: {"Yes — " + phase2.constraints.existing_stack_notes if phase2.constraints.existing_codebase else "No (greenfield)"}
- Budget: {phase2.constraints.budget_range or "not specified"}
- Timeline: {phase2.constraints.timeline or "not specified"}
- Hard constraints:
{constraints_str}

## Interview Summary
{phase2.interview_summary}

---

Generate a complete architecture specification for this project using the \
`generate_architecture_spec` tool.
"""


def build_synthesis_tool() -> dict:
    """
    The tool definition for the synthesis call.
    Claude must fill in every field — this IS the ArchitectSpec schema.
    """
    return {
        "name": "generate_architecture_spec",
        "description": "Generate the complete architecture specification for the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "architecture_style": {
                    "type": "string",
                    "description": "e.g. 'Monolith', 'Microservices', 'Serverless', 'Event-driven'",
                },
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "technology": {"type": "string"},
                            "responsibilities": {"type": "array", "items": {"type": "string"}},
                            "communicates_with": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "description"],
                    },
                },
                "data_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "key_fields": {"type": "array", "items": {"type": "string"}},
                            "relationships": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["name", "description"],
                    },
                },
                "api_endpoints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {"type": "string"},
                            "path": {"type": "string"},
                            "description": {"type": "string"},
                            "request_shape": {"type": "string"},
                            "response_shape": {"type": "string"},
                        },
                        "required": ["path", "description"],
                    },
                },
                "deployment_strategy": {"type": "string"},
                "security_notes": {"type": "array", "items": {"type": "string"}},
                "scalability_notes": {"type": "array", "items": {"type": "string"}},
                "roadmap_phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {"type": "integer"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "primary_agent": {"type": "string"},
                            "agent_rationale": {"type": "string"},
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "estimated_turns": {"type": "integer"},
                                    },
                                    "required": ["title"],
                                },
                            },
                            "estimated_turns_total": {"type": "integer"},
                            "success_criteria": {"type": "array", "items": {"type": "string"}},
                            "checkpoint": {
                                "type": ["object", "null"],
                                "properties": {
                                    "after_task": {"type": "string"},
                                    "turns_used_estimate": {"type": "integer"},
                                    "reason": {"type": "string"},
                                    "resume_prompt": {"type": "string"},
                                },
                            },
                        },
                        "required": ["number", "name", "primary_agent", "tasks"],
                    },
                },
                "decisions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {"type": "integer"},
                            "title": {"type": "string"},
                            "status": {"type": "string"},
                            "context": {"type": "string"},
                            "decision": {"type": "string"},
                            "rationale": {"type": "string"},
                            "trade_offs": {"type": "array", "items": {"type": "string"}},
                            "alternatives_considered": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["number", "title", "context", "decision", "rationale"],
                    },
                },
            },
            "required": [
                "architecture_style",
                "components",
                "roadmap_phases",
                "decisions",
            ],
        },
    }
