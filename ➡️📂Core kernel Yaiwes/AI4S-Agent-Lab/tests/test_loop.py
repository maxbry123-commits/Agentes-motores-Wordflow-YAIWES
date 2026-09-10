import json
import math
import tempfile
import unittest
from pathlib import Path

from ai4s_agent_lab import (
    ExperimentResult,
    JsonlEvidenceLogger,
    Proposal,
    ResearchLoop,
    ScoreValidator,
)
from ai4s_agent_lab.contracts import ValidationResult


class ScriptedProposer:
    def propose(self, state):
        score = (2.0, 1.5)[len(state.history)]
        return Proposal(
            proposal_id=f"candidate-{state.next_iteration}",
            hypothesis="the scripted candidate may improve the score",
            parameters={"score": score},
            rationale="exercise promotion and rollback deterministically",
        )


class EchoScoreTool:
    def run(self, proposal):
        return ExperimentResult(
            proposal_id=proposal.proposal_id,
            score=float(proposal.parameters["score"]),
            metrics={"quality": float(proposal.parameters["score"])},
        )


class ResearchLoopTests(unittest.TestCase):
    def test_before_action_after_records_promotion_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=EchoScoreTool(),
                validator=ScoreValidator(min_delta=0.1),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "loop-test"),
            )
            baseline = Proposal(
                proposal_id="baseline",
                hypothesis="establish a floor",
                parameters={"score": 1.0},
                rationale="known safe reference",
            )

            result = loop.run(
                baseline=baseline,
                iterations=2,
                delivery_path=root / "best.json",
            )

            first, second = result.trials
            self.assertEqual(
                (first.before_score, first.action, first.after_score),
                (1.0, "promote", 2.0),
            )
            self.assertEqual(
                (second.before_score, second.action, second.after_score),
                (2.0, "rollback", 2.0),
            )
            self.assertEqual(result.best_result.score, 2.0)
            delivered = json.loads((root / "best.json").read_text(encoding="utf-8"))
            self.assertEqual(delivered["best_result"]["score"], 2.0)
            self.assertFalse(list(root.glob(".best.json.*.tmp")))

    def test_tool_exception_becomes_a_validator_rollback(self) -> None:
        class FailingTool(EchoScoreTool):
            def run(self, proposal):
                if proposal.proposal_id != "baseline":
                    raise RuntimeError("synthetic failure")
                return super().run(proposal)

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=FailingTool(),
                validator=ScoreValidator(min_delta=0.1),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "failure-test"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "safe reference")
            result = loop.run(
                baseline=baseline,
                iterations=1,
                delivery_path=root / "best.json",
            )
            self.assertEqual(result.trials[0].action, "rollback")
            self.assertFalse(result.trials[0].result.succeeded)
            self.assertEqual(result.best_result.score, 1.0)

    def test_mismatched_tool_evidence_cannot_be_promoted(self) -> None:
        class MismatchedTool(EchoScoreTool):
            def run(self, proposal):
                result = super().run(proposal)
                if proposal.proposal_id == "baseline":
                    return result
                return ExperimentResult(
                    proposal_id="different-proposal",
                    score=result.score,
                    metrics=result.metrics,
                )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=MismatchedTool(),
                validator=ScoreValidator(min_delta=0.1),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "lineage-test"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "safe reference")
            result = loop.run(
                baseline=baseline,
                iterations=1,
                delivery_path=root / "best.json",
            )
            self.assertEqual(result.trials[0].action, "rollback")
            self.assertFalse(result.trials[0].result.succeeded)
            self.assertIn("different proposal", result.trials[0].result.observations[0])
            self.assertEqual(result.best_result.proposal_id, "baseline")

    def test_proposer_cannot_mutate_the_incumbent_snapshot(self) -> None:
        class MutatingProposer:
            def propose(self, state):
                with self.assertRaises(TypeError):
                    state.incumbent.parameters["score"] = 999.0
                return Proposal("candidate", "improve", {"score": 2.0}, "bounded test")

            def __init__(self, test_case):
                self.assertRaises = test_case.assertRaises

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=MutatingProposer(self),
                tool=EchoScoreTool(),
                validator=ScoreValidator(min_delta=0.1),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "immutable-state"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "safe reference")
            result = loop.run(baseline=baseline, iterations=1, delivery_path=root / "best.json")
            self.assertEqual(baseline.parameters["score"], 1.0)
            self.assertEqual(result.best_proposal.parameters["score"], 2.0)

    def test_baseline_uses_metric_bounds_and_explicit_floor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            baseline = Proposal("baseline", "floor", {"score": 2.0}, "reference")
            bounded_loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=EchoScoreTool(),
                validator=ScoreValidator(metric_bounds={"quality": (0.0, 1.5)}),
                logger=JsonlEvidenceLogger(root / "bounded.jsonl", "bounded-floor"),
            )
            with self.assertRaisesRegex(RuntimeError, "floor validator"):
                bounded_loop.run(
                    baseline=baseline,
                    iterations=1,
                    delivery_path=root / "bounded.json",
                )
            self.assertFalse((root / "bounded.json").exists())

            floor_loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=EchoScoreTool(),
                validator=ScoreValidator(),
                logger=JsonlEvidenceLogger(root / "threshold.jsonl", "threshold-floor"),
            )
            with self.assertRaisesRegex(RuntimeError, "below floor_score"):
                floor_loop.run(
                    baseline=baseline,
                    iterations=1,
                    delivery_path=root / "threshold.json",
                    floor_score=10.0,
                )

    def test_nonfinite_candidate_is_rolled_back_and_artifact_remains_valid_json(self) -> None:
        class NonfiniteTool(EchoScoreTool):
            def run(self, proposal):
                if proposal.proposal_id == "baseline":
                    return super().run(proposal)
                return ExperimentResult(
                    proposal_id=proposal.proposal_id,
                    score=3.0,
                    metrics={"quality": math.nan},
                )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=NonfiniteTool(),
                validator=ScoreValidator(),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "nonfinite-result"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "reference")
            result = loop.run(baseline=baseline, iterations=1, delivery_path=root / "best.json")
            self.assertEqual(result.trials[0].action, "rollback")
            self.assertFalse(result.trials[0].result.succeeded)
            self.assertEqual(json.loads((root / "best.json").read_text())["best_result"]["score"], 1.0)

    def test_invalid_validator_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ScoreValidator(min_delta=math.nan)
        with self.assertRaises(ValueError):
            ScoreValidator(metric_bounds={"quality": (2.0, 1.0)})

    def test_extreme_finite_floor_survives_a_tool_failure(self) -> None:
        class ExtremeTool(EchoScoreTool):
            def run(self, proposal):
                if proposal.proposal_id == "baseline":
                    return ExperimentResult(
                        proposal_id="baseline",
                        score=1.0e308,
                        metrics={"quality": 1.0},
                    )
                raise RuntimeError("synthetic failure")

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=ExtremeTool(),
                validator=ScoreValidator(),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "extreme-floor"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0e308}, "reference")
            result = loop.run(baseline=baseline, iterations=1, delivery_path=root / "best.json")
            self.assertTrue(math.isfinite(result.trials[0].validation.delta))
            self.assertEqual(result.trials[0].action, "rollback")
            json.loads((root / "best.json").read_text(encoding="utf-8"))

    def test_contract_booleans_and_validator_output_are_strict(self) -> None:
        with self.assertRaises(ValueError):
            Proposal("/private/proposal", "invalid id", {}, "boundary test")
        with self.assertRaises(TypeError):
            ExperimentResult("candidate", 2.0, {}, succeeded="false")
        with self.assertRaises(TypeError):
            ValidationResult(accepted="false", delta=1.0, reasons=("invalid",))
        with self.assertRaises(TypeError):
            ValidationResult(accepted=False, delta=1.0, reasons=None)

    def test_tool_and_validator_receive_defensive_copies(self) -> None:
        class MutatingTool(EchoScoreTool):
            def run(self, proposal):
                original_id = proposal.proposal_id
                if original_id != "baseline":
                    object.__setattr__(proposal, "proposal_id", "tool-mutated")
                return ExperimentResult(
                    proposal_id=original_id,
                    score=float(proposal.parameters["score"]),
                    metrics={"quality": float(proposal.parameters["score"])},
                )

        class MutatingValidator(ScoreValidator):
            def validate(self, incumbent, candidate):
                decision = super().validate(incumbent, candidate)
                object.__setattr__(candidate, "score", math.nan)
                return decision

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=ScriptedProposer(),
                tool=MutatingTool(),
                validator=MutatingValidator(min_delta=0.1),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "defensive-copies"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "reference")
            result = loop.run(baseline=baseline, iterations=1, delivery_path=root / "best.json")
            self.assertEqual(result.best_proposal.proposal_id, "candidate-1")
            self.assertEqual(result.best_result.proposal_id, "candidate-1")
            self.assertEqual(result.best_result.score, 2.0)

    def test_duplicate_proposal_id_is_recorded_as_failure_and_rolled_back(self) -> None:
        class DuplicateProposer:
            def propose(self, state):
                return Proposal(
                    "baseline",
                    "reuse an ambiguous identifier",
                    {"score": 3.0},
                    "exercise the lineage guard",
                )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            loop = ResearchLoop(
                proposer=DuplicateProposer(),
                tool=EchoScoreTool(),
                validator=ScoreValidator(),
                logger=JsonlEvidenceLogger(root / "evidence.jsonl", "unique-proposals"),
            )
            baseline = Proposal("baseline", "floor", {"score": 1.0}, "reference")
            result = loop.run(baseline=baseline, iterations=1, delivery_path=root / "best.json")
            self.assertEqual(result.trials[0].action, "rollback")
            self.assertTrue(result.trials[0].proposal.proposal_id.startswith("proposal-failure"))


if __name__ == "__main__":
    unittest.main()
