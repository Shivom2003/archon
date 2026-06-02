"""Output generators — one per .architect/ file."""

from archon.generators.architecture_md import ArchitectureGenerator
from archon.generators.base import BaseGenerator
from archon.generators.decisions_md import DecisionsGenerator
from archon.generators.roadmap_md import RoadmapGenerator
from archon.generators.shims import AgentsMdGenerator, ClaudeMdGenerator
from archon.generators.spec_md import SpecGenerator

__all__ = [
    "BaseGenerator",
    "SpecGenerator",
    "ArchitectureGenerator",
    "RoadmapGenerator",
    "DecisionsGenerator",
    "AgentsMdGenerator",
    "ClaudeMdGenerator",
]


def all_generators(spec) -> list[BaseGenerator]:
    """Return one instance of every generator for the given spec."""
    return [
        SpecGenerator(spec),
        ArchitectureGenerator(spec),
        RoadmapGenerator(spec),
        DecisionsGenerator(spec),
        AgentsMdGenerator(spec),
        ClaudeMdGenerator(spec),
    ]
