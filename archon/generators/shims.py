"""
Compatibility shim generators.
AGENTS.md — cross-tool open standard (Sourcegraph/OpenAI/Google/Cursor).
CLAUDE.md  — Claude Code native format.
Both are derived from the ArchitectSpec and kept in sync.
"""

from archon.generators.base import BaseGenerator


class AgentsMdGenerator(BaseGenerator):
    """Generates AGENTS.md — the cross-tool agent instruction standard."""
    template_name = "AGENTS.md.j2"
    output_filename = "AGENTS.md"


class ClaudeMdGenerator(BaseGenerator):
    """Generates CLAUDE.md — Claude Code native format."""
    template_name = "CLAUDE.md.j2"
    output_filename = "CLAUDE.md"
