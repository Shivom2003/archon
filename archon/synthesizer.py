"""
Architecture synthesis pass.

Takes the completed interview data (Phase1 + Phase2) and makes a single
Claude API call to generate the full ArchitectSpec. The synthesis call
uses a different, larger tool schema that maps directly to ArchitectSpec.
"""

from archon.llm.base import LLMClient
from archon.models.enums import AgenticTool
from archon.models.interview import Phase2Data
from archon.models.project import ProjectConfig
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
from archon.plan_registry import get_plan_config
from archon.prompts.synthesizer import (
    build_synthesis_system_prompt,
    build_synthesis_tool,
    build_synthesis_user_prompt,
)


async def synthesize(
    config: ProjectConfig,
    phase2: Phase2Data,
    llm: LLMClient,
) -> ArchitectSpec:
    """
    Run the synthesis pass: call Claude with the full interview data
    and parse the tool call response into an ArchitectSpec.
    """
    system = build_synthesis_system_prompt()
    user_prompt = build_synthesis_user_prompt(config, phase2)
    tool = build_synthesis_tool()

    response = await llm.generate(
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[tool],
        max_tokens=8192,
        cache_system=True,
    )

    # Extract the tool call
    tool_calls = [b for b in response["content"] if b["type"] == "tool_use"]
    if not tool_calls:
        raise RuntimeError(
            "Synthesis failed: Claude did not call generate_architecture_spec. "
            f"Stop reason: {response['stop_reason']}"
        )

    data = tool_calls[0]["input"]
    return _parse_spec(config, phase2, data)


def _parse_spec(
    config: ProjectConfig,
    phase2: Phase2Data,
    data: dict,
) -> ArchitectSpec:
    """Parse the raw tool-call output dict into a typed ArchitectSpec."""

    # Components
    components = [
        SystemComponent(
            name=c["name"],
            description=c.get("description", ""),
            technology=c.get("technology", ""),
            responsibilities=c.get("responsibilities", []),
            communicates_with=c.get("communicates_with", []),
        )
        for c in data.get("components", [])
    ]

    # Data entities
    data_entities = [
        DataEntity(
            name=e["name"],
            description=e.get("description", ""),
            key_fields=e.get("key_fields", []),
            relationships=e.get("relationships", []),
        )
        for e in data.get("data_entities", [])
    ]

    # API endpoints
    api_endpoints = [
        ApiEndpoint(
            method=ep.get("method", ""),
            path=ep["path"],
            description=ep.get("description", ""),
            request_shape=ep.get("request_shape", ""),
            response_shape=ep.get("response_shape", ""),
        )
        for ep in data.get("api_endpoints", [])
    ]

    architecture = ArchitectureData(
        tech_stack=phase2.tech_stack,
        components=components,
        data_entities=data_entities,
        api_endpoints=api_endpoints,
        architecture_style=data.get("architecture_style", "Monolith"),
        deployment_strategy=data.get("deployment_strategy", ""),
        security_notes=data.get("security_notes", []),
        scalability_notes=data.get("scalability_notes", []),
    )

    # Roadmap phases
    phases = []
    for p in data.get("roadmap_phases", []):
        # Resolve agent — default to primary tool if unrecognised
        agent_str = p.get("primary_agent", config.primary_tool.value)
        try:
            agent = AgenticTool(agent_str)
        except ValueError:
            agent = config.primary_tool

        tasks = [
            RoadmapTask(
                title=t["title"],
                description=t.get("description", ""),
                estimated_turns=t.get("estimated_turns", 1),
            )
            for t in p.get("tasks", [])
        ]

        # Parse optional checkpoint
        checkpoint = None
        cp_data = p.get("checkpoint")
        if cp_data and isinstance(cp_data, dict):
            checkpoint = Checkpoint(
                after_task=cp_data.get("after_task", tasks[-1].title if tasks else ""),
                turns_used_estimate=cp_data.get("turns_used_estimate", 0),
                reason=cp_data.get("reason", "Suggested pause point."),
                resume_prompt=cp_data.get("resume_prompt", ""),
            )

        phases.append(
            RoadmapPhase(
                number=p["number"],
                name=p["name"],
                description=p.get("description", ""),
                primary_agent=agent,
                agent_rationale=p.get("agent_rationale", ""),
                tasks=tasks,
                estimated_turns_total=p.get("estimated_turns_total", sum(
                    t.estimated_turns for t in tasks
                )),
                checkpoint=checkpoint,
                success_criteria=p.get("success_criteria", []),
            )
        )

    roadmap = RoadmapData(
        phases=phases,
        core_features=phase2.core_features,
    )

    # ADRs
    decisions = [
        ArchitectureDecision(
            number=d["number"],
            title=d["title"],
            status=d.get("status", "accepted"),
            context=d.get("context", ""),
            decision=d.get("decision", ""),
            rationale=d.get("rationale", ""),
            trade_offs=d.get("trade_offs", []),
            alternatives_considered=d.get("alternatives_considered", []),
        )
        for d in data.get("decisions", [])
    ]

    return ArchitectSpec(
        project=config,
        phase2=phase2,
        architecture=architecture,
        roadmap=roadmap,
        decisions=decisions,
    )
