# Contributing to Archon

Thanks for your interest in contributing! This guide covers everything you need
to go from zero to a merged pull request.

---

## Development Setup

**Requirements:** Python 3.11+, git

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/archon
cd archon

# 2. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 3. Verify everything works
pytest tests/ -v

# 4. Run the linter
ruff check archon/ tests/
ruff format archon/ tests/
```

No virtual environment tool is required — use whatever you prefer (`venv`, `uv`, `pyenv`).

---

## Project Structure

```
archon/
├── models/          Pydantic data models (enums, ProjectConfig, ArchitectSpec)
├── llm/             LLM client abstraction (Claude + registry)
├── prompts/         System prompts and tool schemas for interview + synthesis
├── generators/      Jinja2-based markdown generators
├── templates/       .j2 template files (one per output file)
├── interviewer.py   Two-phase interview engine
├── synthesizer.py   Architecture generation pass
├── session.py       Resumable session state
├── plan_registry.py Usage-limit data per (tool, tier) combo
└── cli.py           Click CLI entry point
```

---

## Common Contribution Types

### Adding a new agentic tool

1. Add the tool to `AgenticTool` enum in `archon/models/enums.py`
   — add a `label` and `strengths` entry
2. Add plan configs to `archon/plan_registry.py` for each known tier
3. Add a test in `tests/test_plan_registry.py`

### Adding a new subscription tier

1. Add to `SubscriptionTier` enum in `archon/models/enums.py`
2. Add entries to `_REGISTRY` in `archon/plan_registry.py`
3. Add a test

### Updating output format (`.j2` templates)

Templates live in `archon/templates/`. Each maps to one output file:

| Template | Output |
|----------|--------|
| `SPEC.md.j2` | `.architect/SPEC.md` |
| `ARCHITECTURE.md.j2` | `.architect/ARCHITECTURE.md` |
| `ROADMAP.md.j2` | `.architect/ROADMAP.md` |
| `DECISIONS.md.j2` | `.architect/DECISIONS.md` |
| `AGENTS.md.j2` | `.architect/AGENTS.md` |
| `CLAUDE.md.j2` | `.architect/CLAUDE.md` |

After editing a template, run `pytest tests/test_generators.py -v` to verify
the output still renders correctly.

### Updating the interview prompts

Interview prompts live in `archon/prompts/interviewer.py`. If you change the
tool schemas (add/remove/rename a tool call), update:
- The tool definition in `PHASE2_TOOLS`
- The handler in `archon/interviewer.py` (`_handle_tool_call`)
- Any affected tests in `tests/test_interviewer.py`

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Single file
pytest tests/test_generators.py -v

# With coverage
pytest tests/ --cov=archon --cov-report=term-missing
```

Tests do **not** make real API calls — the LLM layer is mocked in tests.

---

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check archon/ tests/          # lint
ruff format archon/ tests/         # format
ruff check --fix archon/ tests/    # auto-fix lint issues
```

The CI will reject PRs that fail `ruff check` or `ruff format --check`.

---

## Releasing a New Version (maintainers only)

1. Update `version` in `pyproject.toml`
2. Commit: `git commit -m "chore: bump version to X.Y.Z"`
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. The `publish.yml` workflow will:
   - Run tests
   - Build the wheel + sdist
   - Verify the tag matches `pyproject.toml`
   - Publish to PyPI via OIDC trusted publishing (no token required)
   - Create a GitHub Release with artifacts attached

**First-time PyPI setup:** Configure a Trusted Publisher at
https://pypi.org/manage/account/publishing/ before the first publish.

---

## Questions?

Open a [Discussion](https://github.com/archon-ai/archon/discussions) —
not an Issue — for questions, ideas, and general chat.
