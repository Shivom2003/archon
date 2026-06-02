# Archon

**AI-powered project architecture specification generator for agentic development workflows.**

Archon interviews you about your project, then generates a `.architect/` directory of structured, AI-agent-friendly specification files — including usage-limit-aware checkpoints and multi-agent task assignments.

```
archon init
```

→ produces `.architect/SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `DECISIONS.md`, `AGENTS.md`, `CLAUDE.md`

---

## Why Archon?

Current agentic tools (Claude Code, Codex, Kiro, Cursor) accept project instructions but don't help you *write* them. You either spend hours crafting a CLAUDE.md by hand, or your agent starts coding without sufficient context.

Archon solves this with a two-phase approach:

1. **Structured intake** — 8 questions about project type, scale, tools, and expertise
2. **AI interview** — Claude asks adaptive follow-up questions about your tech stack, features, and constraints

The result is a complete `.architect/` directory that any agentic tool can consume — with two differentiating features no other tool provides:

- **Agent assignment matrix** — tasks distributed across your tools based on each tool's strengths
- **Checkpoint markers** — natural pause points with copy-pasteable resume prompts, calibrated to your subscription tier

---

## Installation

```bash
pip install archon
# or
uv add archon
```

Requires Python 3.11+.

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Quickstart

```bash
# Run the full interview (Phase 1 + Phase 2 + synthesis)
archon init

# View the generated spec in your terminal
archon show

# Re-export a specific file after editing spec.json
archon export --format agents-md

# Re-run the interview to update the spec
archon update

# Validate the spec against the current schema
archon validate
```

---

## Output: `.architect/` Directory

| File | Purpose |
|------|---------|
| `SPEC.md` | Human-readable project overview — goals, features, constraints, magic moment |
| `ARCHITECTURE.md` | Technical architecture — components, data model, API design, security |
| `ROADMAP.md` | Development phases with agent assignments and **checkpoint markers** |
| `DECISIONS.md` | Architecture Decision Records (ADRs) — *why* decisions were made |
| `AGENTS.md` | Cross-tool agent instructions ([AGENTS.md standard](https://hivetrail.com/blog/agents-md-vs-claude-md-cross-tool-standard)) |
| `CLAUDE.md` | Claude Code native format |
| `spec.json` | Machine-readable source of truth (all generators read from this) |

### Example checkpoint in ROADMAP.md

```markdown
> ⚠️ **CHECKPOINT — Claude Code Pro**
> ~8 turns used. Suggested pause point before beginning the API layer.
>
> **Resume prompt:**
> Continue taskflow project. Phase 1 complete (DB schema + migrations passing).
> Begin Phase 2: API Layer. Full context: .architect/ARCHITECTURE.md
```

---

## CLI Reference

```
archon init       [--output-dir PATH] [--model MODEL] [--skip-phase2]
archon show       [--output-dir PATH]
archon update     [--output-dir PATH] [--model MODEL]
archon export     [--output-dir PATH] --format {spec-md,architecture-md,roadmap-md,decisions-md,agents-md,claude-md,all}
archon validate   [--output-dir PATH]
```

---

## Python API

```python
import asyncio
from archon.interviewer import run_phase1, run_phase2
from archon.synthesizer import synthesize
from archon.generators import all_generators
from archon.llm import get_client
from pathlib import Path

async def main():
    config = run_phase1()                     # CLI intake
    llm = get_client("claude-sonnet-4-5")
    phase2 = await run_phase2(config, llm)    # AI interview
    spec = await synthesize(config, phase2, llm)

    for gen in all_generators(spec):
        gen.write(Path(".architect"))

asyncio.run(main())
```

---

## Supported Agentic Tools & Plans

Archon knows the usage limits for the following tools and calibrates checkpoint frequency accordingly:

| Tool | Tiers |
|------|-------|
| Claude Code | Free, Pro, Max, Team, Enterprise, API |
| Codex / ChatGPT | Free, Pro, API |
| Cursor | Free, Pro, Team |
| Kiro (Amazon) | Free, Pro |
| Antigravity | Free, Pro |
| Windsurf | Free, Pro |
| GitHub Copilot | Free, Pro |

---

## Contributing

```bash
git clone https://github.com/archon-ai/archon
cd archon
uv sync --dev
uv run pytest
```

PRs welcome. Please open an issue before starting large changes.

---

## License

MIT — see [LICENSE](LICENSE).

---

*Part of the [Archon](https://archon.dev) project. The Python library is open source.
The hosted product with web UI and team features is available at [archon.dev](https://archon.dev).*
