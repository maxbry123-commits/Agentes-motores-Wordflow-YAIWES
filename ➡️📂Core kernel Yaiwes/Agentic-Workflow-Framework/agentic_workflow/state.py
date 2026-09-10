"""Shared state store passed between workers in a pipeline.

:class:`SharedState` is the single source of truth that every worker reads from
and writes to. It is a thin, JSON-serializable key/value store with an append-
only event log and a monotonically increasing revision counter, which together
make it cheap to checkpoint and to resume.

Design intent:

* Workers never talk to each other directly. They communicate only through keys
  in the shared state. This keeps each worker single-responsibility and makes the
  data-flow auditable.
* :meth:`SharedState.require` is the input-contract primitive: a worker asks for
  the keys it needs and gets a precise :class:`ContractViolation` if an upstream
  step failed to produce them.
* The whole object round-trips through :meth:`to_dict` / :meth:`from_dict`, which
  is what makes clean stop/resume possible.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from .errors import ContractViolation


@dataclass(frozen=True)
class StateEvent:
    """One immutable record of a worker having produced an output.

    The list of events is the workflow's audit trail: which worker ran, where it
    wrote, which version of its (mutable) instruction was active, and what score
    the evaluator gave the result.
    """

    step: str
    worker: str
    output_key: str
    instruction_version: int
    score: Optional[float]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "worker": self.worker,
            "output_key": self.output_key,
            "instruction_version": self.instruction_version,
            "score": self.score,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateEvent":
        return cls(
            step=data["step"],
            worker=data["worker"],
            output_key=data["output_key"],
            instruction_version=data["instruction_version"],
            score=data.get("score"),
            timestamp=data.get("timestamp", 0.0),
        )


class SharedState:
    """A JSON-serializable key/value store shared across a pipeline run."""

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        history: Optional[Iterable[StateEvent]] = None,
        revision: int = 0,
    ) -> None:
        self._data: Dict[str, Any] = dict(data or {})
        self._history: List[StateEvent] = list(history or [])
        self._revision: int = revision

    # -- reads -------------------------------------------------------------
    def has(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def require(self, key: str) -> Any:
        """Return the value for ``key`` or raise a precise contract error.

        This is the input-contract primitive used by workers. It deliberately
        names the missing key so a broken pipeline is easy to diagnose.
        """
        if key not in self._data:
            available = ", ".join(sorted(self._data)) or "<empty>"
            raise ContractViolation(
                f"required state key '{key}' is missing (available: {available})"
            )
        return self._data[key]

    def keys(self) -> List[str]:
        return list(self._data)

    def snapshot(self) -> Dict[str, Any]:
        """Return a deep copy of the data, safe to hand to callers."""
        return copy.deepcopy(self._data)

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def history(self) -> List[StateEvent]:
        return list(self._history)

    # -- writes ------------------------------------------------------------
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._revision += 1

    def update(self, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            self.set(key, value)

    def record(self, event: StateEvent) -> None:
        self._history.append(event)
        self._revision += 1

    # -- serialization -----------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self._data,
            "history": [event.to_dict() for event in self._history],
            "revision": self._revision,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SharedState":
        return cls(
            data=dict(payload.get("data", {})),
            history=[StateEvent.from_dict(e) for e in payload.get("history", [])],
            revision=int(payload.get("revision", 0)),
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"SharedState(keys={sorted(self._data)!r}, "
            f"revision={self._revision}, events={len(self._history)})"
        )
