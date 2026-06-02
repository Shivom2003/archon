"""Tests for plan registry lookups."""

from archon.models.enums import AgenticTool, SubscriptionTier
from archon.plan_registry import get_plan_config, list_supported_plans


def test_known_plan_lookup():
    config = get_plan_config(AgenticTool.CLAUDE_CODE, SubscriptionTier.PRO)
    assert config.turns_per_session == 28
    assert config.checkpoint_every == 8
    assert config.has_limits is True


def test_api_plan_has_no_limits():
    config = get_plan_config(AgenticTool.CLAUDE_CODE, SubscriptionTier.API)
    assert config.has_limits is False


def test_unknown_plan_returns_default():
    config = get_plan_config(AgenticTool.OTHER, SubscriptionTier.FREE)
    # Falls back to default
    assert config.turns_per_session > 0
    assert config.checkpoint_every > 0


def test_all_plans_have_valid_values():
    for plan in list_supported_plans():
        assert plan.turns_per_session > 0
        assert plan.checkpoint_every > 0
        assert plan.checkpoint_every <= plan.turns_per_session
