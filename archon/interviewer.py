"""
Two-phase interview engine.

Phase 1 — Structured Rich CLI intake (8 questions, no LLM needed).
Phase 2 — LLM-driven adaptive interview (Claude uses tool calls to capture data).
"""

import asyncio
from typing import Any

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from archon.llm.base import LLMClient
from archon.models.enums import (
    AgenticTool,
    ConsumerScale,
    DevScale,
    ExpertiseLevel,
    ProjectType,
    SubscriptionTier,
)
from archon.models.interview import (
    CoreFeature,
    Phase2Data,
    ProjectConstraints,
    TechStack,
)
from archon.models.project import ProjectConfig, ToolSubscription
from archon.prompts.interviewer import PHASE2_TOOLS, build_phase2_system_prompt
from archon.session import InterviewSession, SessionState

console = Console()

# ── Phase 1 helpers ──────────────────────────────────────────────────────────


def _enum_select(prompt: str, enum_cls: type, allow_multiple: bool = False) -> Any:
    """
    Render a numbered menu from an enum's values and return the selection(s).
    """
    members = list(enum_cls)
    table = Table(show_header=False, box=None, padding=(0, 2))
    for i, member in enumerate(members, 1):
        table.add_row(f"[cyan]{i}[/cyan]", member.label)
    console.print(table)

    if allow_multiple:
        raw = Prompt.ask(
            f"[bold]{prompt}[/bold] [dim](comma-separated numbers)[/dim]"
        )
        indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip().isdigit()]
        return [members[i] for i in indices if 0 <= i < len(members)]
    else:
        while True:
            raw = Prompt.ask(f"[bold]{prompt}[/bold] [dim](enter number)[/dim]")
            if raw.isdigit() and 1 <= int(raw) <= len(members):
                return members[int(raw) - 1]
            console.print("[red]Invalid choice. Try again.[/red]")


def run_phase1() -> ProjectConfig:
    """Run Phase 1: structured CLI intake. Returns a populated ProjectConfig."""
    console.print(
        Panel(
            "[bold cyan]Archon — Project Architecture Interviewer[/bold cyan]\n"
            "[dim]Phase 1 of 2 — Structured intake (no AI needed)[/dim]",
            expand=False,
        )
    )
    console.print()

    # Q1 — Identity
    console.print("[bold]1/8  Project identity[/bold]")
    name = Prompt.ask("  Project name [dim](short, no spaces — used as package/dir name)[/dim]")
    description = Prompt.ask("  One-sentence description")
    console.print()

    # Q2 — Project type
    console.print("[bold]2/8  What type of project is this?[/bold]")
    project_type: ProjectType = _enum_select("Select type", ProjectType)
    console.print()

    # Q3 — Consumer scale
    console.print("[bold]3/8  Consumer scale — how many end-users?[/bold]")
    consumer_scale: ConsumerScale = _enum_select("Select scale", ConsumerScale)
    console.print()

    # Q4 — Dev scale
    console.print("[bold]4/8  Dev scale — who's building this?[/bold]")
    dev_scale: DevScale = _enum_select("Select dev scale", DevScale)
    console.print()

    # Q5 — Agentic tools
    console.print("[bold]5/8  Which agentic tools will you use?[/bold]")
    agentic_tools: list[AgenticTool] = _enum_select(
        "Select tools", AgenticTool, allow_multiple=True
    )
    if not agentic_tools:
        agentic_tools = [AgenticTool.CLAUDE_CODE]
        console.print("[dim]No tools selected — defaulting to Claude Code.[/dim]")
    console.print()

    # Q6 — Multi-agent distribution
    distribute = False
    if len(agentic_tools) > 1:
        console.print("[bold]6/8  Multi-agent task distribution[/bold]")
        distribute = Confirm.ask(
            "  Distribute development tasks across your selected tools?",
            default=True,
        )
    else:
        console.print("[dim]6/8  Skipping multi-agent distribution (only 1 tool selected)[/dim]")
    console.print()

    # Q7 — Subscription tiers
    console.print("[bold]7/8  Subscription tiers (for checkpoint planning)[/bold]")
    subscriptions: list[ToolSubscription] = []
    for tool in agentic_tools:
        console.print(f"  [cyan]{tool.label}[/cyan] — what plan are you on?")
        tier: SubscriptionTier = _enum_select(f"  {tool.label} tier", SubscriptionTier)
        subscriptions.append(ToolSubscription(tool=tool, tier=tier))
    console.print()

    # Q8 — Expertise
    console.print("[bold]8/8  Your expertise level[/bold]")
    expertise: ExpertiseLevel = _enum_select("Select level", ExpertiseLevel)
    console.print()

    config = ProjectConfig(
        name=name,
        description=description,
        project_type=project_type,
        consumer_scale=consumer_scale,
        dev_scale=dev_scale,
        agentic_tools=agentic_tools,
        distribute_across_agents=distribute,
        tool_subscriptions=subscriptions,
        expertise_level=expertise,
    )

    console.print(
        Panel(
            f"[green]Phase 1 complete![/green]\n"
            f"Project: [bold]{config.name}[/bold] — {config.description}",
            expand=False,
        )
    )
    return config


# ── Phase 2 helpers ──────────────────────────────────────────────────────────

MAX_TURNS = 12  # Hard cap to prevent runaway conversations


async def run_phase2(config: ProjectConfig, llm: LLMClient) -> Phase2Data:
    """
    Run Phase 2: LLM-driven adaptive interview.
    Claude uses tool calls to build up Phase2Data incrementally.
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]Phase 2 — AI-Driven Interview[/bold cyan]\n"
            "[dim]Claude will ask follow-up questions about your tech stack, features, and constraints.[/dim]",
            expand=False,
        )
    )
    console.print()

    system = build_phase2_system_prompt(config)
    phase2 = Phase2Data()
    messages: list[dict] = []
    turns = 0

    # Kick off the interview
    messages.append({
        "role": "user",
        "content": (
            "I've completed the intake form. Please start the interview by asking me "
            "about my tech stack first."
        ),
    })

    while turns < MAX_TURNS:
        turns += 1
        with console.status("[dim]Claude is thinking...[/dim]", spinner="dots"):
            response = await llm.generate(
                system=system,
                messages=messages,
                tools=PHASE2_TOOLS,
                max_tokens=1024,
                cache_system=True,  # Cache the large system prompt
            )

        # Process tool calls in the response
        tool_calls = [b for b in response["content"] if b["type"] == "tool_use"]
        text_blocks = [b for b in response["content"] if b["type"] == "text"]

        # Display Claude's conversational text
        for block in text_blocks:
            if block["text"].strip():
                console.print(f"\n[bold blue]Archon:[/bold blue] {block['text'].strip()}\n")
                phase2.add_turn("assistant", block["text"])

        # Process tool calls (silent — they update phase2 state)
        tool_results = []
        interview_complete = False

        for tc in tool_calls:
            result, done = _handle_tool_call(tc["name"], tc["input"], phase2, config)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": result,
            })
            if done:
                interview_complete = True

        # Add assistant turn + tool results to history
        messages.append({"role": "assistant", "content": response["content"]})
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        if interview_complete:
            console.print(
                Panel(
                    "[green]Phase 2 complete![/green] Interview finished.",
                    expand=False,
                )
            )
            break

        # If no tool calls and stop_reason is end_turn, interview stalled — ask user
        if not tool_calls and response["stop_reason"] == "end_turn":
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if not user_input.strip():
                continue
            messages.append({"role": "user", "content": user_input})
            phase2.add_turn("user", user_input)

    else:
        console.print("[yellow]Interview turn limit reached — proceeding with gathered data.[/yellow]")

    return phase2


def _handle_tool_call(
    name: str,
    inputs: dict,
    phase2: Phase2Data,
    config: ProjectConfig,
) -> tuple[str, bool]:
    """
    Apply a tool call to the Phase2Data object.
    Returns (result_message, is_complete).
    """
    match name:
        case "record_tech_stack":
            stack = phase2.tech_stack
            stack.languages = list(set(stack.languages + inputs.get("languages", [])))
            stack.frameworks = list(set(stack.frameworks + inputs.get("frameworks", [])))
            stack.databases = list(set(stack.databases + inputs.get("databases", [])))
            stack.infra_cloud = list(set(stack.infra_cloud + inputs.get("infra_cloud", [])))
            stack.other = list(set(stack.other + inputs.get("other", [])))
            return "Tech stack recorded.", False

        case "record_constraints":
            from archon.models.enums import ComplianceRequirement
            c = phase2.constraints
            if "compliance" in inputs:
                c.compliance = [ComplianceRequirement(v) for v in inputs["compliance"]]
            if "existing_codebase" in inputs:
                c.existing_codebase = inputs["existing_codebase"]
            if "existing_stack_notes" in inputs:
                c.existing_stack_notes = inputs["existing_stack_notes"]
            if "budget_range" in inputs:
                c.budget_range = inputs["budget_range"]
            if "timeline" in inputs:
                c.timeline = inputs["timeline"]
            if "key_constraints" in inputs:
                c.key_constraints = inputs["key_constraints"]
            return "Constraints recorded.", False

        case "record_core_feature":
            from archon.models.enums import Priority
            feature = CoreFeature(
                name=inputs["name"],
                description=inputs["description"],
                priority=Priority(inputs["priority"]),
            )
            # Avoid duplicates
            existing_names = {f.name.lower() for f in phase2.core_features}
            if feature.name.lower() not in existing_names:
                phase2.core_features.append(feature)
            return f"Feature '{feature.name}' recorded.", False

        case "record_magic_moment":
            phase2.magic_moment = inputs["magic_moment"]
            return "Magic moment recorded.", False

        case "complete_interview":
            phase2.interview_summary = inputs["summary"]
            return "Interview complete.", True

        case _:
            return f"Unknown tool: {name}", False
