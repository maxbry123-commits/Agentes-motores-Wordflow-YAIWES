"""Small, dependency-free contracts for an auditable research loop."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, fields, is_dataclass
from types import MappingProxyType
from typing import Any, Mapping, Protocol


Scalar = str | int | float | bool | None
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _frozen_mapping(value: Mapping[str, Scalar]) -> Mapping[str, Scalar]:
    """Copy a scalar mapping behind a read-only proxy."""

    copied: dict[str, Scalar] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError("mapping keys must be non-empty strings")
        if item is not None and not isinstance(item, (str, int, float, bool)):
            raise TypeError(f"unsupported scalar value for {key}")
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError(f"floating-point parameter must be finite: {key}")
        copied[key] = item
    return MappingProxyType(copied)


def to_plain_data(value: Any) -> Any:
    """Convert contracts and read-only mappings to JSON-compatible data."""

    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: to_plain_data(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): to_plain_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain_data(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported value type: {type(value).__name__}")


@dataclass(frozen=True)
class Proposal:
    """A testable hypothesis and the parameters needed to evaluate it."""

    proposal_id: str
    hypothesis: str
    parameters: Mapping[str, Scalar]
    rationale: str

    def __post_init__(self) -> None:
        for name in ("proposal_id", "hypothesis", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not _SAFE_IDENTIFIER.fullmatch(self.proposal_id):
            raise ValueError("proposal_id must be a short, path-free identifier")
        object.__setattr__(self, "parameters", _frozen_mapping(self.parameters))


@dataclass(frozen=True)
class ExperimentResult:
    """Structured output from a scientific tool invocation.

    Scores use a higher-is-better convention. Domain tools can transform a
    minimization objective (for example RMSE) into a score such as ``-RMSE``.
    """

    proposal_id: str
    score: float
    metrics: Mapping[str, float]
    observations: tuple[str, ...] = ()
    succeeded: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        if not _SAFE_IDENTIFIER.fullmatch(self.proposal_id):
            raise ValueError("proposal_id must be a short, path-free identifier")
        if not isinstance(self.score, (int, float)) or isinstance(self.score, bool):
            raise TypeError("score must be numeric")
        object.__setattr__(self, "score", float(self.score))
        copied_metrics: dict[str, float] = {}
        for key, value in self.metrics.items():
            if not isinstance(key, str) or not key:
                raise ValueError("metric keys must be non-empty strings")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"metric must be numeric: {key}")
            copied_metrics[key] = float(value)
        if not isinstance(self.succeeded, bool):
            raise TypeError("succeeded must be a bool")
        object.__setattr__(self, "metrics", MappingProxyType(copied_metrics))
        object.__setattr__(self, "observations", tuple(str(item) for item in self.observations))


@dataclass(frozen=True)
class ValidationResult:
    """The validator's explicit decision about a candidate experiment."""

    accepted: bool
    delta: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool")
        if not isinstance(self.delta, (int, float)) or isinstance(self.delta, bool):
            raise TypeError("delta must be numeric")
        if not isinstance(self.reasons, tuple) or not self.reasons:
            raise TypeError("reasons must be a non-empty tuple")
        if not all(isinstance(reason, str) and reason for reason in self.reasons):
            raise TypeError("each validation reason must be a non-empty string")
        object.__setattr__(self, "delta", float(self.delta))


@dataclass(frozen=True)
class TrialRecord:
    """Before -> Action -> After evidence for one iteration."""

    iteration: int
    proposal: Proposal
    result: ExperimentResult
    validation: ValidationResult
    action: str
    before_score: float
    candidate_score: float
    after_score: float


@dataclass(frozen=True)
class StateView:
    """Read-only state supplied to a proposer."""

    run_id: str
    next_iteration: int
    incumbent: Proposal
    incumbent_result: ExperimentResult
    floor_score: float
    history: tuple[TrialRecord, ...] = ()


@dataclass(frozen=True)
class RunSummary:
    """Final result delivered by the loop."""

    run_id: str
    floor_score: float
    best_proposal: Proposal
    best_result: ExperimentResult
    trials: tuple[TrialRecord, ...] = field(default_factory=tuple)


class Proposer(Protocol):
    """Generate the next testable hypothesis from the current evidence."""

    def propose(self, state: StateView) -> Proposal:
        """Return the next proposal without mutating ``state``."""


class ExperimentTool(Protocol):
    """Run one proposal and return a structured measurement."""

    def run(self, proposal: Proposal) -> ExperimentResult:
        """Evaluate ``proposal``."""


class Validator(Protocol):
    """Check whether a candidate is safe and better than the incumbent."""

    def validate_floor(self, candidate: ExperimentResult) -> ValidationResult:
        """Check whether a baseline is a valid comparison point."""

    def validate(
        self,
        incumbent: ExperimentResult,
        candidate: ExperimentResult,
    ) -> ValidationResult:
        """Return an evidence-backed promotion decision."""
