"""agentic_workflow — a lightweight multi-agent workflow framework.

A stateful :class:`Manager` orchestrates single-responsibility :class:`Worker`
agents through a :class:`Pipeline`, communicating via a :class:`SharedState`
store, with clean stop/resume through :class:`CheckpointStore` and an optional
self-improvement loop that refines a worker's *mutable* instruction without ever
touching its protected core.

See the README for the full architecture overview.
"""

from __future__ import annotations

from .checkpoint import CheckpointStore
from .errors import (
    AgenticWorkflowError,
    BackendError,
    CheckpointError,
    ContractViolation,
    ProtectedCoreError,
)
from .improvement import improve_instruction
from .llm import (
    DEFAULT_MODEL,
    AnthropicBackend,
    LLMBackend,
    LLMResponse,
    MockLLMBackend,
)
from .manager import Manager
from .pipeline import EvalResult, Evaluator, Pipeline, Step
from .state import SharedState, StateEvent
from .worker import PROTOCOL_RULES, Worker, WorkerResult

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # orchestration
    "Manager",
    "Pipeline",
    "Step",
    "EvalResult",
    "Evaluator",
    # workers
    "Worker",
    "WorkerResult",
    "PROTOCOL_RULES",
    # state & persistence
    "SharedState",
    "StateEvent",
    "CheckpointStore",
    # backends
    "LLMBackend",
    "LLMResponse",
    "AnthropicBackend",
    "MockLLMBackend",
    "DEFAULT_MODEL",
    # self-improvement
    "improve_instruction",
    # errors
    "AgenticWorkflowError",
    "ContractViolation",
    "ProtectedCoreError",
    "CheckpointError",
    "BackendError",
]
