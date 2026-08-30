"""A synthetic exponential-decay calibration case study.

The example is intentionally small and dependency-free. It demonstrates loop
mechanics; it is not competition code or a claim about a production model.
"""

from __future__ import annotations

import math
import uuid
from pathlib import Path

from .contracts import ExperimentResult, Proposal, RunSummary, StateView
from .evidence import JsonlEvidenceLogger
from .loop import ResearchLoop
from .validation import ScoreValidator


TRUE_RATE = 0.42
TIME_POINTS = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)
NOISE = (0.0, 0.012, -0.008, 0.006, -0.004, 0.003, -0.002)


class DecayExperimentTool:
    """Measure how well a candidate rate fits a fixed synthetic dataset."""

    amplitude = 2.5

    def __init__(self) -> None:
        self.measurements = tuple(
            self.amplitude * math.exp(-TRUE_RATE * time) + noise
            for time, noise in zip(TIME_POINTS, NOISE, strict=True)
        )

    def run(self, proposal: Proposal) -> ExperimentResult:
        rate_value = proposal.parameters.get("decay_rate")
        if not isinstance(rate_value, (int, float)) or isinstance(rate_value, bool):
            raise ValueError("decay_rate must be numeric")
        rate = float(rate_value)
        if rate <= 0.0:
            raise ValueError("decay_rate must be positive")

        predictions = tuple(self.amplitude * math.exp(-rate * time) for time in TIME_POINTS)
        mse = sum(
            (observed - predicted) ** 2
            for observed, predicted in zip(self.measurements, predictions, strict=True)
        ) / len(TIME_POINTS)
        rmse = math.sqrt(mse)
        return ExperimentResult(
            proposal_id=proposal.proposal_id,
            score=-rmse,
            metrics={
                "rmse": rmse,
                "half_life": math.log(2.0) / rate,
                "sample_count": float(len(TIME_POINTS)),
            },
            observations=("evaluated against a fixed synthetic decay series",),
        )


class BracketSearchProposer:
    """A deterministic hill-climber that learns direction from rollbacks."""

    def __init__(
        self,
        *,
        parameter: str,
        initial_step: float,
        lower: float,
        upper: float,
        shrink: float = 0.5,
    ) -> None:
        if not (0.0 < shrink < 1.0):
            raise ValueError("shrink must be between zero and one")
        self.parameter = parameter
        self.initial_step = initial_step
        self.lower = lower
        self.upper = upper
        self.shrink = shrink

    def propose(self, state: StateView) -> Proposal:
        direction = 1.0
        step = self.initial_step
        for trial in state.history:
            if trial.action == "rollback":
                direction *= -1.0
                step *= self.shrink

        current_value = state.incumbent.parameters[self.parameter]
        if not isinstance(current_value, (int, float)) or isinstance(current_value, bool):
            raise TypeError(f"incumbent parameter must be numeric: {self.parameter}")
        candidate_value = min(self.upper, max(self.lower, float(current_value) + direction * step))
        return Proposal(
            proposal_id=f"trial-{state.next_iteration:03d}",
            hypothesis=(
                f"changing {self.parameter} from {float(current_value):.4f} "
                f"to {candidate_value:.4f} will improve fit quality"
            ),
            parameters={self.parameter: candidate_value},
            rationale=(
                "continue in the last productive direction; reverse and shrink the step "
                "after a validator rollback"
            ),
        )


def run_demo(
    output_dir: str | Path,
    *,
    iterations: int = 6,
    run_id: str | None = None,
) -> RunSummary:
    """Run the toy case and write evidence plus the verified best artifact."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    effective_run_id = run_id or f"decay-{uuid.uuid4().hex[:12]}"
    logger = JsonlEvidenceLogger(destination / "evidence.jsonl", effective_run_id)
    loop = ResearchLoop(
        proposer=BracketSearchProposer(
            parameter="decay_rate",
            initial_step=0.20,
            lower=0.05,
            upper=1.20,
        ),
        tool=DecayExperimentTool(),
        validator=ScoreValidator(
            min_delta=1e-6,
            metric_bounds={
                "rmse": (0.0, 1.0),
                "half_life": (0.25, 5.0),
                "sample_count": (float(len(TIME_POINTS)), float(len(TIME_POINTS))),
            },
        ),
        logger=logger,
    )
    baseline = Proposal(
        proposal_id="baseline",
        hypothesis="a low initial decay rate provides a measurable floor",
        parameters={"decay_rate": 0.15},
        rationale="start from a deliberately coarse, valid reference point",
    )
    return loop.run(
        baseline=baseline,
        iterations=iterations,
        delivery_path=destination / "best_model.json",
    )
