"""Exception hierarchy for the agentic workflow framework.

All framework errors derive from :class:`AgenticWorkflowError`, so callers can
catch the whole family with a single ``except`` while still being able to branch
on the specific failure mode.
"""

from __future__ import annotations


class AgenticWorkflowError(Exception):
    """Base class for every error raised by this framework."""


class ContractViolation(AgenticWorkflowError):
    """A worker's input or output contract was not satisfied.

    Raised when a required key is absent from the shared state, or when an LLM
    response does not match the worker's declared output schema. This is the
    guard that the *protected core* enforces and that mutable instructions can
    never disable.
    """


class ProtectedCoreError(AgenticWorkflowError):
    """A subclass attempted to override a protected-core method.

    The protected core (input validation, prompt assembly, output validation,
    state writes) is the part of a worker that the self-improvement loop is not
    allowed to touch. Overriding it would let a "tuning" change silently break
    the I/O protocol, so it is rejected at class-definition time.
    """


class CheckpointError(AgenticWorkflowError):
    """A checkpoint could not be written, read, or validated."""


class BackendError(AgenticWorkflowError):
    """The language-model backend failed or returned an unusable response."""
