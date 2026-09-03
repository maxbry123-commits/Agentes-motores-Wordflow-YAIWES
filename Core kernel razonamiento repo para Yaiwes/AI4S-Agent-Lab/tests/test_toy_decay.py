import json
import tempfile
import unittest
from pathlib import Path

from ai4s_agent_lab.toy_decay import TRUE_RATE, run_demo


class ToyDecayTests(unittest.TestCase):
    def test_demo_improves_the_floor_and_keeps_rejected_trials_out(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            result = run_demo(root, iterations=6, run_id="deterministic-demo")

            best_rate = float(result.best_proposal.parameters["decay_rate"])
            self.assertLessEqual(abs(best_rate - TRUE_RATE), 0.05)
            self.assertGreater(result.best_result.score, result.floor_score)
            self.assertIn("promote", {trial.action for trial in result.trials})
            self.assertIn("rollback", {trial.action for trial in result.trials})
            self.assertTrue((root / "best_model.json").is_file())

            events = [
                json.loads(line)
                for line in (root / "evidence.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(events[0]["event"], "run_started")
            self.assertEqual(events[1]["stage"], "floor")
            self.assertEqual(events[-1]["stage"], "delivery")
            self.assertEqual([event["sequence"] for event in events], list(range(1, len(events) + 1)))

    def test_same_run_configuration_produces_identical_best_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first"
            second = root / "second"
            run_demo(first, iterations=6, run_id="repeatable-demo")
            run_demo(second, iterations=6, run_id="repeatable-demo")
            self.assertEqual(
                (first / "best_model.json").read_bytes(),
                (second / "best_model.json").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
