"""The Manager: a stateful orchestrator over a pipeline of workers.

The Manager owns everything dynamic about a run:

* the shared state,
* the cursor (which step runs next),
* the per-worker mutable instruction snapshots,
* an execution log.

It drives the pipeline one step at a time, optionally checkpointing after each
step so a run can be stopped and resumed cleanly. When a step has an evaluator
and the score falls short, the Manager runs the self-improvement loop on that
step's worker — refining the worker's *mutable instruction* only, never its
protected core.

Typical usage::

    manager = Manager(pipeline, backend, checkpoint_store=store, run_id="ticket-42")
    manager.run(max_steps=2)            # stop early
    # ... later, in a fresh process ...
    manager = Manager.resume(pipeline, backend, store, "ticket-42")
    manager.run()                       # finish the rest
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from .checkpoint import CheckpointStore
from .errors import CheckpointError
from .improvement import improve_instruction
from .llm import LLMBackend
from .pipeline import EvalResult, Pipeline, Step
from .state import SharedState, StateEvent
from .worker import WorkerResult


class Manager:
    """Stateful orchestrator for a :class:`Pipeline`."""

    def __init__(
        self,
        pipeline: Pipeline,
        backend: LLMBackend,
        *,
        state: Optional[SharedState] = None,
        checkpoint_store: Optional[CheckpointStore] = None,
        run_id: Optional[str] = None,
        max_improvement_rounds: int = 2,
    ) -> None:
        self.pipeline = pipeline
        self.backend = backend
        self.state = state or SharedState()
        self.checkpoints = checkpoint_store
        self.run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        self.max_improvement_rounds = max_improvement_rounds
        self.cursor = 0
        self.log: List[Dict[str, Any]] = []

    # -- progress ----------------------------------------------------------
    @property
    def is_done(self) -> bool:
        return self.cursor >= len(self.pipeline)

    @property
    def next_step_name(self) -> Optional[str]:
        if self.is_done:
            return None
        return self.pipeline.step_at(self.cursor).name

    # -- execution ---------------------------------------------------------
    def step(self) -> Optional[WorkerResult]:
        """Run exactly the step at the cursor, advance, and checkpoint.

        Returns the step's (best) :class:`WorkerResult`, or ``None`` if the
        pipeline is already finished.
        """
        if self.is_done:
            return None

        step = self.pipeline.step_at(self.cursor)
        result, evaluation = self._execute_step(step)

        self.state.record(
            StateEvent(
                step=step.name,
                worker=step.worker.name,
                output_key=step.worker.output_key,
                instruction_version=step.worker.instruction_version,
                score=evaluation.score if evaluation else None,
                timestamp=time.time(),
            )
        )
        self.cursor += 1
        if self.checkpoints is not None:
            self.checkpoint()
        return result

    def run(
        self,
        *,
        max_steps: Optional[int] = None,
        stop_before: Optional[str] = None,
    ) -> SharedState:
        """Run steps until done, or until a stop condition is reached.

        Args:
            max_steps: Run at most this many steps this call (then return).
            stop_before: Stop *before* running the step with this worker name.

        Returns the shared state, so callers can read results inline.
        """
        executed = 0
        while not self.is_done:
            if max_steps is not None and executed >= max_steps:
                break
            if stop_before is not None and self.next_step_name == stop_before:
                break
            self.step()
            executed += 1
        return self.state

    def _execute_step(
        self, step: Step
    ) -> Tuple[WorkerResult, Optional[EvalResult]]:
        """Run a step and, if it has an evaluator, the self-improvement loop.

        Self-improvement is bounded by ``max_improvement_rounds``. Each round
        asks the backend for a better instruction (which only the worker's
        ``propose_instruction`` may accept) and re-runs the worker. The best
        result seen is the one that survives, and the shared state is reconciled
        to that best result at the end — so a regression never leaks downstream.
        """
        worker = step.worker
        best_result = worker.run(self.state, self.backend)
        best_eval = step.evaluator(best_result, self.state) if step.evaluator else None

        if step.evaluator is None or best_eval is None:
            return best_result, best_eval

        rounds = 0
        while (
            best_eval.score < step.improve_threshold
            and rounds < self.max_improvement_rounds
        ):
            rounds += 1
            proposal = improve_instruction(
                self.backend, worker, best_result, best_eval
            )
            accepted = bool(proposal) and worker.propose_instruction(proposal)  # type: ignore[arg-type]
            if not accepted:
                # Model gave nothing usable; further rounds won't help.
                self.log.append(
                    {
                        "event": "improvement_rejected",
                        "worker": worker.name,
                        "round": rounds,
                        "score": best_eval.score,
                    }
                )
                break

            candidate_result = worker.run(self.state, self.backend)
            candidate_eval = step.evaluator(candidate_result, self.state)
            self.log.append(
                {
                    "event": "improvement_round",
                    "worker": worker.name,
                    "round": rounds,
                    "instruction_version": worker.instruction_version,
                    "score_before": best_eval.score,
                    "score_after": candidate_eval.score,
                }
            )
            if candidate_eval.score >= best_eval.score:
                best_result, best_eval = candidate_result, candidate_eval
            # else: keep the previous best; loop may try once more.

        # Reconcile shared state to the best result we actually kept.
        self.state.set(worker.output_key, best_result.output)
        return best_result, best_eval

    # -- checkpointing -----------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialize everything needed to resume this run."""
        return {
            "run_id": self.run_id,
            "cursor": self.cursor,
            "max_improvement_rounds": self.max_improvement_rounds,
            "pipeline": self.pipeline.names,
            "state": self.state.to_dict(),
            "workers": {
                step.name: step.worker.instruction_state()
                for step in self.pipeline
            },
            "log": self.log,
            "saved_at": time.time(),
        }

    def checkpoint(self, name: Optional[str] = None) -> None:
        """Persist the current run under ``name`` (defaults to ``run_id``)."""
        if self.checkpoints is None:
            raise CheckpointError("no checkpoint store configured on this manager")
        self.checkpoints.save(name or self.run_id, self.to_dict())

    @classmethod
    def resume(
        cls,
        pipeline: Pipeline,
        backend: LLMBackend,
        checkpoint_store: CheckpointStore,
        name: str,
    ) -> "Manager":
        """Reconstruct a Manager from a saved checkpoint.

        The provided ``pipeline`` must structurally match the one that was saved
        (same worker names, same order). The saved mutable instructions are
        restored onto the pipeline's workers, so any self-improvement that
        happened before the stop is carried forward.
        """
        payload = checkpoint_store.load(name)

        saved_names = payload.get("pipeline", [])
        if saved_names != pipeline.names:
            raise CheckpointError(
                "pipeline mismatch on resume: checkpoint has "
                f"{saved_names}, pipeline has {pipeline.names}"
            )

        manager = cls(
            pipeline,
            backend,
            state=SharedState.from_dict(payload["state"]),
            checkpoint_store=checkpoint_store,
            run_id=payload["run_id"],
            max_improvement_rounds=payload.get("max_improvement_rounds", 2),
        )
        manager.cursor = int(payload.get("cursor", 0))
        manager.log = list(payload.get("log", []))

        for worker_name, snapshot in payload.get("workers", {}).items():
            pipeline.worker_by_name(worker_name).restore_instruction(snapshot)

        return manager

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"Manager(run_id={self.run_id!r}, "
            f"cursor={self.cursor}/{len(self.pipeline)}, "
            f"next={self.next_step_name!r})"
        )
