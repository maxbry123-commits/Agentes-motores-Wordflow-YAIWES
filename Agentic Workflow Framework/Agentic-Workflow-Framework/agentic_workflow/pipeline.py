"""Pipeline definition: an ordered list of evaluated steps.

A :class:`Pipeline` is the *static* description of a workflow — which workers run
and in what order, and how (optionally) each one's output is scored. The dynamic
cursor that walks the pipeline lives on the :class:`~agentic_workflow.manager.Manager`,
which keeps the pipeline reusable and easy to checkpoint.

An evaluator is any callable ``(WorkerResult, SharedState) -> EvalResult``. When
a step's evaluator returns a score below ``improve_threshold``, the Manager runs
its self-improvement loop on that step's worker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional

from .state import SharedState
from .worker import Worker, WorkerResult


@dataclass
class EvalResult:
    """A quality judgement for one worker output.

    ``score`` is normalized to ``[0, 1]``; ``feedback`` is free text that the
    self-improvement loop feeds back to the model so it knows *why* the output
    fell short.
    """

    score: float
    feedback: str = ""

    def __post_init__(self) -> None:
        # Clamp defensively so a misbehaving evaluator can't poison the loop.
        self.score = max(0.0, min(1.0, float(self.score)))


Evaluator = Callable[[WorkerResult, SharedState], EvalResult]


@dataclass
class Step:
    """One worker plus its optional quality gate."""

    worker: Worker
    evaluator: Optional[Evaluator] = None
    #: If an evaluator scores strictly below this, trigger self-improvement.
    improve_threshold: float = 0.0

    @property
    def name(self) -> str:
        return self.worker.name


class Pipeline:
    """An ordered, name-unique collection of steps."""

    def __init__(self, steps: List[Step]) -> None:
        if not steps:
            raise ValueError("a pipeline needs at least one step")
        names = [step.name for step in steps]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            raise ValueError(
                f"worker names must be unique within a pipeline; "
                f"duplicates: {', '.join(sorted(duplicates))}"
            )
        self._steps: List[Step] = list(steps)
        self._by_name: Dict[str, Step] = {step.name: step for step in steps}

    @property
    def names(self) -> List[str]:
        return [step.name for step in self._steps]

    def step_at(self, index: int) -> Step:
        return self._steps[index]

    def index_of(self, name: str) -> int:
        return self.names.index(name)

    def worker_by_name(self, name: str) -> Worker:
        return self._by_name[name].worker

    def __len__(self) -> int:
        return len(self._steps)

    def __iter__(self) -> Iterator[Step]:
        return iter(self._steps)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Pipeline({' -> '.join(self.names)})"
