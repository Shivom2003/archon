"""Tests for Pydantic models and enums."""

import pytest
from pydantic import ValidationError

from archon.models.enums import (
    AgenticTool,
    ConsumerScale,
    ExpertiseLevel,
    ProjectType,
    SubscriptionTier,
)
from archon.models.project import ProjectConfig, ToolSubscription


def test_project_config_valid(sample_config):
    assert sample_config.name == "taskflow"
    assert sample_config.primary_tool == AgenticTool.CLAUDE_CODE


def test_project_config_requires_at_least_one_tool():
    with pytest.raises(ValidationError):
        ProjectConfig(
            name="test",
            description="test",
            project_type=ProjectType.API_SERVICE,
            consumer_scale=ConsumerScale.SMALL_TEAM,
            dev_scale="solo",
            agentic_tools=[],  # empty — should fail
            expertise_level=ExpertiseLevel.INTERMEDIATE,
        )


def test_get_subscription(sample_config):
    tier = sample_config.get_subscription(AgenticTool.CLAUDE_CODE)
    assert tier == SubscriptionTier.PRO
    assert sample_config.get_subscription(AgenticTool.CURSOR) is None


def test_tool_subscription_str():
    sub = ToolSubscription(tool=AgenticTool.CLAUDE_CODE, tier=SubscriptionTier.PRO)
    assert "Claude Code" in str(sub)
    assert "Pro" in str(sub)


def test_agentic_tool_strengths():
    strengths = AgenticTool.CLAUDE_CODE.strengths
    assert isinstance(strengths, list)
    assert len(strengths) > 0


def test_enum_labels():
    assert ProjectType.WEB_APP.label == "Web Application"
    assert ConsumerScale.ENTERPRISE.label.startswith("Enterprise")
    assert ExpertiseLevel.NOVICE.label.startswith("Novice")


def test_spec_serialisation(sample_spec):
    """ArchitectSpec round-trips through JSON without loss."""
    from archon.models.spec import ArchitectSpec

    json_str = sample_spec.to_json()
    restored = ArchitectSpec.from_json(json_str)
    assert restored.project.name == sample_spec.project.name
    assert len(restored.decisions) == len(sample_spec.decisions)
    assert len(restored.roadmap.phases) == len(sample_spec.roadmap.phases)
