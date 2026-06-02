"""Tests for the markdown generators."""

from archon.generators import (
    AgentsMdGenerator,
    ArchitectureGenerator,
    ClaudeMdGenerator,
    DecisionsGenerator,
    RoadmapGenerator,
    SpecGenerator,
    all_generators,
)


def test_spec_generator_renders(sample_spec):
    output = SpecGenerator(sample_spec).render()
    assert "taskflow" in output
    assert "Magic Moment" in output
    assert "Task CRUD" in output


def test_architecture_generator_renders(sample_spec):
    output = ArchitectureGenerator(sample_spec).render()
    assert "Monolith" in output
    assert "FastAPI" in output
    assert "PostgreSQL" in output
    assert "API Server" in output


def test_roadmap_generator_renders(sample_spec):
    output = RoadmapGenerator(sample_spec).render()
    assert "Phase 1" in output
    assert "Foundation" in output
    assert "CHECKPOINT" in output
    assert "resume_prompt" not in output.lower()  # resume prompt is in a code block
    assert "Continue taskflow" in output


def test_decisions_generator_renders(sample_spec):
    output = DecisionsGenerator(sample_spec).render()
    assert "ADR-001" in output
    assert "Monolith over microservices" in output
    assert "Rationale" in output


def test_agents_md_generator_renders(sample_spec):
    output = AgentsMdGenerator(sample_spec).render()
    assert "AGENTS.md" in output
    assert "taskflow" in output
    assert "ADR-001" in output


def test_claude_md_generator_renders(sample_spec):
    output = ClaudeMdGenerator(sample_spec).render()
    assert "CLAUDE.md" in output
    assert "taskflow" in output
    assert "magic moment" in output.lower()


def test_all_generators_write(sample_spec, tmp_path):
    """all_generators writes all 6 expected files."""
    gens = all_generators(sample_spec)
    assert len(gens) == 6

    for gen in gens:
        path = gen.write(tmp_path)
        assert path.exists()
        assert path.stat().st_size > 100  # non-trivial content


def test_roadmap_checkpoint_content(sample_spec):
    """Checkpoint resume prompt appears in ROADMAP.md."""
    output = RoadmapGenerator(sample_spec).render()
    assert "Continue taskflow project" in output
    assert "⚠️" in output


def test_spec_generator_no_features(sample_spec):
    """Generator handles empty features list gracefully."""
    sample_spec.phase2.core_features = []
    output = SpecGenerator(sample_spec).render()
    assert "no features captured" in output
