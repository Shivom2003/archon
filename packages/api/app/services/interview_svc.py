"""
Interview service — bridges the HTTP layer and the archon library.

Phase 1: validates the form submission into a ProjectConfig.
Phase 2: manages the multi-turn LLM conversation state and emits SSE events.
"""

import json
import logging
from collections.abc import AsyncGenerator

from archon.llm.registry import get_client
from archon.models.enums import AgenticTool, ExpertiseLevel, ProjectType, ConsumerScale, DevScale, SubscriptionTier
from archon.models.interview import CoreFeature, Phase2Data
from archon.models.project import ProjectConfig, ToolSubscription
from archon.prompts.interviewer import PHASE2_TOOLS, build_phase2_system_prompt
from app.schemas import Phase1Submit

logger = logging.getLogger(__name__)

# Maximum turns before forcibly completing Phase 2
MAX_TURNS = 12


# ── Phase 1 ───────────────────────────────────────────────────────────────────


def validate_phase1(body: Phase1Submit) -> ProjectConfig:
    """
    Convert the web form submission into a validated ProjectConfig.
    Raises ValueError with a user-friendly message on invalid input.
    """
    try:
        tools = [AgenticTool(t) for t in body.agentic_tools]
        subs = [
            ToolSubscription(tool=AgenticTool(s["tool"]), tier=SubscriptionTier(s["tier"]))
            for s in body.tool_subscriptions
        ]
        return ProjectConfig(
            name=body.name,
            description=body.description,
            project_type=ProjectType(body.project_type),
            consumer_scale=ConsumerScale(body.consumer_scale),
            dev_scale=DevScale(body.dev_scale),
            agentic_tools=tools,
            distribute_across_agents=body.distribute_across_agents,
            tool_subscriptions=subs,
            expertise_level=ExpertiseLevel(body.expertise_level),
        )
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid Phase 1 data: {e}") from e


# ── Phase 2 SSE ───────────────────────────────────────────────────────────────


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE data line."""
    return f"data: {json.dumps(data)}\n\n"


async def run_phase2_turn(
    config: ProjectConfig,
    phase2: Phase2Data,
    messages: list[dict],
    user_message: str | None,
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Run a single Phase 2 turn and yield SSE events.

    On each call:
    - If user_message is provided, append it to messages first.
    - Call Claude, stream text tokens and handle tool calls.
    - Yield SSE events for each piece of output.
    - Mutate phase2 in place with captured tool-call data.
    - Yield a "question_complete" or "interview_complete" event to signal the turn end.

    Returns (phase2, messages, is_done) via the generator's StopIteration value —
    callers should collect the updated state from the phase2 object reference.
    """
    from archon.interviewer import _handle_tool_call  # noqa: PLC0415

    llm = get_client(model)
    system = build_phase2_system_prompt(config)

    # Add user message if this isn't the first turn
    if user_message is not None:
        messages.append({"role": "user", "content": user_message})
        phase2.add_turn("user", user_message)

    try:
        response = await llm.generate(
            system=system,
            messages=messages,
            tools=PHASE2_TOOLS,
            max_tokens=1024,
            cache_system=True,
        )
    except Exception as exc:
        yield _sse_event({"type": "error", "message": str(exc)})
        return

    # Stream text content
    text_blocks = [b for b in response["content"] if b["type"] == "text"]
    tool_calls = [b for b in response["content"] if b["type"] == "tool_use"]

    for block in text_blocks:
        text = block["text"].strip()
        if text:
            yield _sse_event({"type": "text", "content": text})
            phase2.add_turn("assistant", text)

    # Process tool calls silently, emit a summary event for each
    tool_results = []
    interview_complete = False

    for tc in tool_calls:
        result, done = _handle_tool_call(tc["name"], tc["input"], phase2, config)
        tool_results.append({"type": "tool_result", "tool_use_id": tc["id"], "content": result})
        # Emit a tool_call event so the frontend can show live feedback
        yield _sse_event({"type": "tool_call", "name": tc["name"], "result": result})
        if done:
            interview_complete = True

    # Update messages history
    messages.append({"role": "assistant", "content": response["content"]})
    if tool_results:
        messages.append({"role": "user", "content": tool_results})

    if interview_complete:
        yield _sse_event({"type": "interview_complete"})
    else:
        yield _sse_event({"type": "question_complete"})
