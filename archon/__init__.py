"""
Archon — AI-powered project architecture specification generator.

Public API:
    from archon import Interviewer, synthesize, ArchitectSpec
"""

from archon.models.spec import ArchitectSpec
from archon.synthesizer import synthesize

__version__ = "0.1.0"
__all__ = ["ArchitectSpec", "synthesize", "__version__"]
