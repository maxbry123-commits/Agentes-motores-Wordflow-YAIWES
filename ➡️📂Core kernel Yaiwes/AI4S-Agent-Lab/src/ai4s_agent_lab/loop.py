"""An inspectable floor -> propose -> experiment -> validate research loop."""

from __future__ import annotations

import math
from pathlib import Path

from .artifacts import AtomicArtifactWriter
from .contracts import (
    ExperimentResult,
    ExperimentTool,
    Proposal,
    Proposer,
    RunSummary,
    StateView,
    TrialRecord,
    ValidationResult,
    Validator,
)
from .evidence import JsonlEvidenceLogger
from .validation import finite_score_delta


class ResearchLoop:
    """Coordinate experiments while keeping promotion decisions explicit."""

    def __init__(
        self,
        *,
        proposer: Proposer,
        tool: ExperimentTool,
        validator: Validator,
        logger: JsonlEvidenceLogger,
        artifact_writer: AtomicArtifactWriter | None = None,
    ) -> None:
        self.proposer = proposer
        self.tool = tool
        self.validator = validator
        self.logger = logger
        self.artifact_writer = artifact_writer or AtomicArtifactWriter()

    def run(
        self,
        *,
        baseline: Proposal,
        iterations: int,
        delivery_path: str | Path,
        floor_score: float | None = None,
    ) -> RunSummary:
        """Run a bounded loop and atomically deliver the best verified state."""

        if not isinstance(iterations, int) or isinstance(iterations, bool) or iterations < 1:
            raise ValueError("iterations must be at least one")
        if floor_score is not None and (
            not isinstance(floor_score, (int, float))
            or isinstance(floor_score, bool)
            or not math.isfinite(floor_score)
        ):
            raise ValueError("floor_score must be finite")

        baseline = _copy_proposal(baseline)
        self.logger.begin_run({"iterations": iterations})
        incumbent_result = self._establish_floor(baseline)
        effective_floor = incumbent_result.score if floor_score is None else floor_score
        if incumbent_result.score < effective_floor:
            self.logger.record(
                "baseline_rejected",
                "floor",
                {"reason": "baseline score is below floor_score"},
            )
            raise RuntimeError("baseline score is below floor_score")

        incumbent = baseline
        proposal_ids = {baseline.proposal_id}
        history: list[TrialRecord] = []
        self.logger.record(
            "floor_established",
            "floor",
            {
                "proposal": baseline,
                "result": incumbent_result,
                "floor_score": effective_floor,
            },
        )

        for iteration in range(1, iterations + 1):
            state = _copy_state(
                run_id=self.logger.run_id,
                next_iteration=iteration,
                incumbent=incumbent,
                incumbent_result=incumbent_result,
                floor_score=effective_floor,
                history=history,
            )
            candidate, proposal_failed = self._propose_candidate(
                state,
                iteration,
                proposal_ids,
            )
            proposal_ids.add(candidate.proposal_id)
            if proposal_failed:
                candidate_result = _failed_result(candidate, "proposer failure")
                self.logger.record(
                    "experiment_skipped",
                    "tool",
                    {"iteration": iteration, "reason": "proposal was invalid"},
                )
            else:
                candidate_result = self._run_candidate(candidate, iteration)
            validation = self._validate_candidate(incumbent_result, candidate_result)

            before_score = incumbent_result.score
            if validation.accepted:
                incumbent = candidate
                incumbent_result = candidate_result
                action = "promote"
            else:
                action = "rollback"

            record = TrialRecord(
                iteration=iteration,
                proposal=candidate,
                result=candidate_result,
                validation=validation,
                action=action,
                before_score=before_score,
                candidate_score=candidate_result.score,
                after_score=incumbent_result.score,
            )
            history.append(record)
            self.logger.record(
                "candidate_decided",
                "validator",
                {
                    "iteration": iteration,
                    "validation": validation,
                    "action": action,
                    "before_score": before_score,
                    "candidate_score": candidate_result.score,
                    "after_score": incumbent_result.score,
                },
            )

        summary = RunSummary(
            run_id=self.logger.run_id,
            floor_score=effective_floor,
            best_proposal=incumbent,
            best_result=incumbent_result,
            trials=tuple(history),
        )
        delivered = self.artifact_writer.write_json(delivery_path, summary)
        artifact_sha256 = self.artifact_writer.verify_json(delivered, summary)
        self.logger.record(
            "artifact_delivered",
            "delivery",
            {
                "delivery_path": delivered,
                "best_score": summary.best_result.score,
                "artifact_sha256": artifact_sha256,
                "promotions": sum(item.action == "promote" for item in history),
                "rollbacks": sum(item.action == "rollback" for item in history),
            },
        )
        return summary

    def _establish_floor(self, baseline: Proposal) -> ExperimentResult:
        try:
            result = self.tool.run(_copy_proposal(baseline))
        except Exception as error:
            self.logger.record(
                "baseline_failed",
                "floor",
                {"error_type": type(error).__name__},
            )
            raise RuntimeError("baseline experiment failed") from error
        if not isinstance(result, ExperimentResult):
            self.logger.record(
                "baseline_failed",
                "floor",
                {"reason": "invalid result type"},
            )
            raise RuntimeError("baseline tool returned an invalid result type")
        result = _copy_result(result)
        if result.proposal_id != baseline.proposal_id:
            self.logger.record(
                "baseline_failed",
                "floor",
                {"reason": "proposal lineage mismatch"},
            )
            raise RuntimeError("baseline result does not match the baseline proposal")
        structural_reasons = _structural_result_reasons(result)
        try:
            validation = _copy_validation(
                self.validator.validate_floor(_copy_result(result))
            )
        except Exception as error:
            self.logger.record(
                "baseline_failed",
                "floor",
                {"error_type": type(error).__name__},
            )
            raise RuntimeError("baseline validator failed") from error
        reasons = [*structural_reasons]
        if not validation.accepted:
            reasons.extend(validation.reasons)
        if reasons:
            self.logger.record(
                "baseline_rejected",
                "floor",
                {"reasons": tuple(dict.fromkeys(reasons))},
            )
            raise RuntimeError("baseline did not pass the floor validator")
        return result

    def _propose_candidate(
        self,
        state: StateView,
        iteration: int,
        proposal_ids: set[str],
    ) -> tuple[Proposal, bool]:
        try:
            candidate = _copy_proposal(self.proposer.propose(state))
            if candidate.proposal_id in proposal_ids:
                raise ValueError("proposal_id must be unique within a run")
        except Exception as error:
            failure_id = f"proposal-failure-{iteration:03d}"
            while failure_id in proposal_ids:
                failure_id += "-fallback"
            candidate = Proposal(
                proposal_id=failure_id,
                hypothesis="the proposer did not return a valid bounded proposal",
                parameters={},
                rationale="retain the validated incumbent after proposer failure",
            )
            self.logger.record(
                "proposal_failed",
                "proposal",
                {"iteration": iteration, "error_type": type(error).__name__},
            )
            return candidate, True
        self.logger.record(
            "proposal_created",
            "proposal",
            {"iteration": iteration, "proposal": candidate},
        )
        return candidate, False

    def _run_candidate(self, candidate: Proposal, iteration: int) -> ExperimentResult:
        try:
            raw_result = self.tool.run(_copy_proposal(candidate))
        except Exception as error:
            result = _failed_result(candidate, f"tool failure: {type(error).__name__}")
        else:
            if not isinstance(raw_result, ExperimentResult):
                result = _failed_result(candidate, "tool returned an invalid result type")
            else:
                try:
                    result = _copy_result(raw_result)
                except (TypeError, ValueError, OverflowError):
                    result = _failed_result(candidate, "tool returned a malformed result")
        if result.proposal_id != candidate.proposal_id:
            result = _failed_result(candidate, "tool returned evidence for a different proposal")
        elif _structural_result_reasons(result):
            result = _failed_result(candidate, "; ".join(_structural_result_reasons(result)))
        self.logger.record(
            "experiment_completed",
            "tool",
            {"iteration": iteration, "result": result},
        )
        return result

    def _validate_candidate(
        self,
        incumbent: ExperimentResult,
        candidate: ExperimentResult,
    ) -> ValidationResult:
        computed_delta = finite_score_delta(candidate.score, incumbent.score)
        try:
            raw_validation = _copy_validation(
                self.validator.validate(
                    _copy_result(incumbent),
                    _copy_result(candidate),
                )
            )
        except Exception as error:
            self.logger.record(
                "validator_failed",
                "validator",
                {"error_type": type(error).__name__},
            )
            return ValidationResult(
                accepted=False,
                delta=computed_delta,
                reasons=("validator raised an exception",),
            )

        safety_reasons = _structural_result_reasons(candidate)
        if computed_delta < 0.0:
            safety_reasons.append("candidate score regressed")
        if not math.isfinite(raw_validation.delta):
            safety_reasons.append("validator delta is not finite")
        if raw_validation.accepted and safety_reasons:
            return ValidationResult(
                accepted=False,
                delta=computed_delta,
                reasons=tuple(dict.fromkeys(safety_reasons)),
            )
        return ValidationResult(
            accepted=raw_validation.accepted,
            delta=computed_delta,
            reasons=tuple(str(reason) for reason in raw_validation.reasons),
        )


def _copy_proposal(value: Proposal) -> Proposal:
    if not isinstance(value, Proposal):
        raise TypeError("proposer must return a Proposal")
    return Proposal(
        proposal_id=value.proposal_id,
        hypothesis=value.hypothesis,
        parameters=dict(value.parameters),
        rationale=value.rationale,
    )


def _copy_result(value: ExperimentResult) -> ExperimentResult:
    return ExperimentResult(
        proposal_id=value.proposal_id,
        score=float(value.score),
        metrics=dict(value.metrics),
        observations=tuple(value.observations),
        succeeded=value.succeeded,
    )


def _copy_validation(value: ValidationResult) -> ValidationResult:
    if not isinstance(value, ValidationResult):
        raise TypeError("validator must return a ValidationResult")
    return ValidationResult(
        accepted=value.accepted,
        delta=value.delta,
        reasons=value.reasons,
    )


def _copy_state(
    *,
    run_id: str,
    next_iteration: int,
    incumbent: Proposal,
    incumbent_result: ExperimentResult,
    floor_score: float,
    history: list[TrialRecord],
) -> StateView:
    copied_history = tuple(
        TrialRecord(
            iteration=record.iteration,
            proposal=_copy_proposal(record.proposal),
            result=_copy_result(record.result),
            validation=ValidationResult(
                accepted=record.validation.accepted,
                delta=record.validation.delta,
                reasons=tuple(record.validation.reasons),
            ),
            action=record.action,
            before_score=record.before_score,
            candidate_score=record.candidate_score,
            after_score=record.after_score,
        )
        for record in history
    )
    return StateView(
        run_id=run_id,
        next_iteration=next_iteration,
        incumbent=_copy_proposal(incumbent),
        incumbent_result=_copy_result(incumbent_result),
        floor_score=floor_score,
        history=copied_history,
    )


def _structural_result_reasons(result: ExperimentResult) -> list[str]:
    reasons: list[str] = []
    if not result.succeeded:
        reasons.append("experiment tool reported failure")
    if not math.isfinite(result.score):
        reasons.append("candidate score is not finite")
    for metric, value in result.metrics.items():
        if not math.isfinite(value):
            reasons.append(f"metric is not finite: {metric}")
    return reasons


def _failed_result(proposal: Proposal, reason: str) -> ExperimentResult:
    return ExperimentResult(
        proposal_id=proposal.proposal_id,
        score=-1.0e308,
        metrics={},
        observations=(reason,),
        succeeded=False,
    )
