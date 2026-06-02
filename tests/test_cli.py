"""Tests for the Click CLI."""

import json

import pytest
from click.testing import CliRunner

from archon.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "archon" in result.output.lower()


def test_cli_init_help(runner):
    result = runner.invoke(main, ["init", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output


def test_cli_show_missing_spec(runner, tmp_path):
    result = runner.invoke(main, ["show", "--output-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "archon init" in result.output


def test_cli_validate_valid_spec(runner, tmp_path, sample_spec):
    """validate succeeds when spec.json is present and valid."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(sample_spec.to_json(), encoding="utf-8")

    result = runner.invoke(main, ["validate", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Valid" in result.output


def test_cli_export_agents_md(runner, tmp_path, sample_spec):
    """export --format agents-md writes AGENTS.md."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(sample_spec.to_json(), encoding="utf-8")

    result = runner.invoke(
        main, ["export", "--output-dir", str(tmp_path), "--format", "agents-md"]
    )
    assert result.exit_code == 0
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    assert "taskflow" in agents_md.read_text()


def test_cli_export_all(runner, tmp_path, sample_spec):
    """export --format all writes all 6 files."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(sample_spec.to_json(), encoding="utf-8")

    result = runner.invoke(
        main, ["export", "--output-dir", str(tmp_path), "--format", "all"]
    )
    assert result.exit_code == 0
    expected_files = ["SPEC.md", "ARCHITECTURE.md", "ROADMAP.md", "DECISIONS.md", "AGENTS.md", "CLAUDE.md"]
    for fname in expected_files:
        assert (tmp_path / fname).exists(), f"{fname} was not written"
