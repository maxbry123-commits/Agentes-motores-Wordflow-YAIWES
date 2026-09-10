"""Exceptions for agent-resume."""

from __future__ import annotations


class AgentResumeError(Exception):
    """Base class for all agent-resume errors."""


class CheckpointCorrupt(AgentResumeError):
    """Raised when a checkpoint store contains a line that cannot be parsed.

    The library is conservative about silently dropping data; if a JSONL file
    has a partial or malformed line the caller usually wants to know rather
    than restart with stale state.
    """

    def __init__(self, message: str, *, line_number: int | None = None) -> None:
        super().__init__(message)
        self.line_number = line_number


class NoCheckpoint(AgentResumeError):
    """Raised by `Store.load_latest()` when there is no checkpoint to load.

    Most callers go through `resume_or_start()` which catches this and starts
    fresh, so you only see it if you reach for the store API directly.
    """
