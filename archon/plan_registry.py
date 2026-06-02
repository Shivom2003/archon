"""
Plan Registry — maps (AgenticTool, SubscriptionTier) → PlanConfig.

PlanConfig tells the roadmap generator:
  - How many agent turns a user roughly gets per session before hitting a limit
  - How frequently to insert checkpoint markers

Data is intentionally conservative (lower than advertised limits) to avoid
the agent getting cut off mid-task. Update this as plan limits change.
"""

from pydantic import BaseModel, Field

from archon.models.enums import AgenticTool, SubscriptionTier


class PlanConfig(BaseModel):
    """Configuration for a specific (tool, tier) combination."""

    tool: AgenticTool
    tier: SubscriptionTier
    turns_per_session: int = Field(
        description="Conservative estimate of turns before a usage limit is hit"
    )
    checkpoint_every: int = Field(
        description="Insert a checkpoint marker every N turns in the roadmap"
    )
    notes: str = Field(default="", description="Human-readable notes about this plan")

    @property
    def has_limits(self) -> bool:
        """True if this plan has meaningful usage limits (not API or enterprise)."""
        return self.turns_per_session < 500


# ---------------------------------------------------------------------------
# Registry: (tool, tier) → PlanConfig
# ---------------------------------------------------------------------------
# fmt: off
_REGISTRY: dict[tuple[AgenticTool, SubscriptionTier], PlanConfig] = {

    # ── Claude Code ──────────────────────────────────────────────────────────
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.FREE,
        turns_per_session=10, checkpoint_every=3,
        notes="Very limited free tier — checkpoint aggressively.",
    ),
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.PRO,
        turns_per_session=28, checkpoint_every=8,
        notes="Claude Pro: ~5-hour rolling window. ~30 turns conservatively.",
    ),
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.MAX): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.MAX,
        turns_per_session=100, checkpoint_every=25,
        notes="Claude Max: 5× higher limits than Pro.",
    ),
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.TEAM): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.TEAM,
        turns_per_session=80, checkpoint_every=20,
    ),
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.ENTERPRISE): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.ENTERPRISE,
        turns_per_session=500, checkpoint_every=100,
        notes="Enterprise plans vary — checkpoints are advisory only.",
    ),
    (AgenticTool.CLAUDE_CODE, SubscriptionTier.API): PlanConfig(
        tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.API,
        turns_per_session=999, checkpoint_every=50,
        notes="Direct API: rate-limited by tokens/min, not turns. Checkpoints advisory.",
    ),

    # ── Codex / ChatGPT ──────────────────────────────────────────────────────
    (AgenticTool.CODEX, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.CODEX, tier=SubscriptionTier.FREE,
        turns_per_session=5, checkpoint_every=2,
        notes="Free Codex tier is very restricted.",
    ),
    (AgenticTool.CODEX, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.CODEX, tier=SubscriptionTier.PRO,
        turns_per_session=50, checkpoint_every=12,
    ),
    (AgenticTool.CODEX, SubscriptionTier.API): PlanConfig(
        tool=AgenticTool.CODEX, tier=SubscriptionTier.API,
        turns_per_session=999, checkpoint_every=50,
    ),

    # ── Cursor ───────────────────────────────────────────────────────────────
    (AgenticTool.CURSOR, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.CURSOR, tier=SubscriptionTier.FREE,
        turns_per_session=50, checkpoint_every=15,
        notes="Cursor free: 50 'fast' requests/month, then slow mode.",
    ),
    (AgenticTool.CURSOR, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.CURSOR, tier=SubscriptionTier.PRO,
        turns_per_session=200, checkpoint_every=40,
        notes="Cursor Pro: 500 fast requests/month.",
    ),
    (AgenticTool.CURSOR, SubscriptionTier.TEAM): PlanConfig(
        tool=AgenticTool.CURSOR, tier=SubscriptionTier.TEAM,
        turns_per_session=200, checkpoint_every=40,
    ),

    # ── Kiro (Amazon) ────────────────────────────────────────────────────────
    (AgenticTool.KIRO, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.KIRO, tier=SubscriptionTier.FREE,
        turns_per_session=50, checkpoint_every=15,
        notes="Kiro free preview tier (limits subject to change).",
    ),
    (AgenticTool.KIRO, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.KIRO, tier=SubscriptionTier.PRO,
        turns_per_session=200, checkpoint_every=40,
    ),

    # ── Antigravity ──────────────────────────────────────────────────────────
    (AgenticTool.ANTIGRAVITY, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.ANTIGRAVITY, tier=SubscriptionTier.FREE,
        turns_per_session=20, checkpoint_every=5,
    ),
    (AgenticTool.ANTIGRAVITY, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.ANTIGRAVITY, tier=SubscriptionTier.PRO,
        turns_per_session=100, checkpoint_every=20,
    ),

    # ── Windsurf ─────────────────────────────────────────────────────────────
    (AgenticTool.WINDSURF, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.WINDSURF, tier=SubscriptionTier.FREE,
        turns_per_session=20, checkpoint_every=5,
    ),
    (AgenticTool.WINDSURF, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.WINDSURF, tier=SubscriptionTier.PRO,
        turns_per_session=150, checkpoint_every=30,
    ),

    # ── GitHub Copilot ───────────────────────────────────────────────────────
    (AgenticTool.COPILOT, SubscriptionTier.FREE): PlanConfig(
        tool=AgenticTool.COPILOT, tier=SubscriptionTier.FREE,
        turns_per_session=2000, checkpoint_every=200,
        notes="Copilot free: 2000 completions/month. Checkpoints advisory.",
    ),
    (AgenticTool.COPILOT, SubscriptionTier.PRO): PlanConfig(
        tool=AgenticTool.COPILOT, tier=SubscriptionTier.PRO,
        turns_per_session=999, checkpoint_every=100,
        notes="Copilot Pro: unlimited completions. Checkpoints advisory.",
    ),
}
# fmt: on

# Default fallback when a (tool, tier) combo isn't in the registry
_DEFAULT_CONFIG = PlanConfig(
    tool=AgenticTool.OTHER,
    tier=SubscriptionTier.PRO,
    turns_per_session=30,
    checkpoint_every=10,
    notes="Unknown plan — using conservative defaults.",
)


def get_plan_config(tool: AgenticTool, tier: SubscriptionTier) -> PlanConfig:
    """
    Look up the PlanConfig for a given (tool, tier) combination.
    Falls back to a conservative default if the combo isn't registered.
    """
    return _REGISTRY.get((tool, tier), _DEFAULT_CONFIG)


def list_supported_plans() -> list[PlanConfig]:
    """Return all registered plan configurations."""
    return list(_REGISTRY.values())
