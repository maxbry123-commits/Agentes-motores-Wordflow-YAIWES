"""Deterministic promotion gates for scientific experiments."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from .contracts import ExperimentResult, ValidationResult


def finite_score_delta(candidate_score: float, incumbent_score: float) -> float:
    """Subtract finite scores without emitting an infinite JSON value."""

    difference = candidate_score - incumbent_score
    if math.isfinite(difference):
        return difference
    return sys.float_info.max if candidate_score >= incumbent_score else -sys.float_info.max


@dataclass(frozen=True)
class ScoreValidator:
    """Require valid measurements, metric bounds, and score improvement."""

    min_delta: float = 0.0
    minimum_score: float | None = None
    metric_bounds: Mapping[str, tuple[float | None, float | None]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not math.isfinite(self.min_delta) or self.min_delta < 0.0:
            raise ValueError("min_delta must be finite and non-negative")
        if self.minimum_score is not None and not math.isfinite(self.minimum_score):
            raise ValueError("minimum_score must be finite")

        copied_bounds: dict[str, tuple[float | None, float | None]] = {}
        for metric, bounds in self.metric_bounds.items():
            if not isinstance(metric, str) or not metric:
                raise ValueError("metric-bound keys must be non-empty strings")
            if len(bounds) != 2:
                raise ValueError(f"metric bound must contain lower and upper: {metric}")
            lower, upper = bounds
            if lower is not None and not math.isfinite(lower):
                raise ValueError(f"metric lower bound must be finite: {metric}")
            if upper is not None and not math.isfinite(upper):
                raise ValueError(f"metric upper bound must be finite: {metric}")
            if lower is not None and upper is not None and lower > upper:
                raise ValueError(f"metric lower bound exceeds upper bound: {metric}")
            copied_bounds[metric] = (lower, upper)
        object.__setattr__(self, "metric_bounds", MappingProxyType(copied_bounds))

    def validate_floor(self, candidate: ExperimentResult) -> ValidationResult:
        """Validate a baseline without requiring improvement over itself."""

        reasons = self._measurement_reasons(candidate)
        if reasons:
            return ValidationResult(accepted=False, delta=0.0, reasons=tuple(reasons))
        return ValidationResult(
            accepted=True,
            delta=0.0,
            reasons=("baseline passed the same measurement constraints",),
        )

    def validate(
        self,
        incumbent: ExperimentResult,
        candidate: ExperimentResult,
    ) -> ValidationResult:
        reasons = self._measurement_reasons(candidate)
        delta = finite_score_delta(candidate.score, incumbent.score)

        if not incumbent.succeeded or not math.isfinite(incumbent.score):
            reasons.append("incumbent is not a valid comparison point")
        if delta <= self.min_delta:
            reasons.append(
                f"score improvement must be greater than min_delta={self.min_delta:g}"
            )

        if reasons:
            return ValidationResult(accepted=False, delta=delta, reasons=tuple(reasons))
        return ValidationResult(
            accepted=True,
            delta=delta,
            reasons=("candidate passed constraints and improved the score",),
        )

    def _measurement_reasons(self, candidate: ExperimentResult) -> list[str]:
        reasons: list[str] = []
        if not candidate.succeeded:
            reasons.append("experiment tool reported failure")
        if not math.isfinite(candidate.score):
            reasons.append("candidate score is not finite")
        if self.minimum_score is not None and candidate.score < self.minimum_score:
            reasons.append("candidate score is below the safety floor")

        for metric, measured in candidate.metrics.items():
            if not math.isfinite(measured):
                reasons.append(f"metric is not finite: {metric}")

        for metric, (lower, upper) in self.metric_bounds.items():
            measured = candidate.metrics.get(metric)
            if measured is None:
                reasons.append(f"required metric is missing: {metric}")
                continue
            if not math.isfinite(measured):
                continue
            if lower is not None and measured < lower:
                reasons.append(f"metric is below lower bound: {metric}")
            elif upper is not None and measured > upper:
                reasons.append(f"metric is above upper bound: {metric}")
        return reasons
