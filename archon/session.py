"""
InterviewSession — manages the state of a complete interview + synthesis run.
Serialisable to JSON for resuming interrupted sessions.
"""

import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from archon.models.interview import Phase2Data
from archon.models.project import ProjectConfig
from archon.models.spec import ArchitectSpec


class SessionState(StrEnum):
    PHASE1 = "phase1"           # Collecting structured intake
    PHASE2 = "phase2"           # LLM-driven interview in progress
    SYNTHESIZING = "synthesizing"  # Running synthesis pass
    COMPLETE = "complete"       # Spec generated successfully
    FAILED = "failed"           # Unrecoverable error


class InterviewSession(BaseModel):
    """
    Full state of an interview session.
    Saved to .architect/session.json so interrupted sessions can be resumed.
    """

    session_id: str = Field(default_factory=lambda: _new_id())
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    state: SessionState = SessionState.PHASE1

    # Set after Phase 1
    config: ProjectConfig | None = None

    # Built up during Phase 2
    phase2: Phase2Data = Field(default_factory=Phase2Data)

    # Set after synthesis
    spec: ArchitectSpec | None = None

    # Error info if state == FAILED
    error: str = ""

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "session.json"
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, output_dir: Path) -> "InterviewSession | None":
        path = output_dir / "session.json"
        if not path.exists():
            return None
        return cls.model_validate_json(path.read_text(encoding="utf-8"))


def _new_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]
