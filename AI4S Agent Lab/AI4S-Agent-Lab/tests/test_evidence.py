import json
import tempfile
import threading
import unittest
from pathlib import Path

from ai4s_agent_lab.evidence import JsonlEvidenceLogger


class EvidenceLoggerTests(unittest.TestCase):
    def test_sensitive_values_are_redacted_before_disk_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "evidence.jsonl"
            logger = JsonlEvidenceLogger(path, "redaction-test")
            fake_bearer = "Bearer " + "abcdefghijkl" + "mnopqrstuvwxyz"
            fake_private_path = str(Path("/") / "Users" / "example" / "private" / "result.json")

            class UnsafeRepr:
                def __repr__(self) -> str:
                    return f"stored at {fake_private_path}"

            logger.record(
                "example",
                "tool",
                {
                    "api_key": "do-not-publish",
                    "prompt": "private chain of thought",
                    "delivery_path": fake_private_path,
                    "message": fake_bearer,
                    f"key saved at {fake_private_path}": "sensitive key",
                    "embedded_path": f"result was written to {fake_private_path} before delivery",
                    "unknown": UnsafeRepr(),
                    "token_count": 42,
                    "public_url": "https://example.org/results/run-1",
                    "safe": "public measurement",
                },
            )

            raw = path.read_text(encoding="utf-8")
            self.assertNotIn("do-not-publish", raw)
            self.assertNotIn("private chain of thought", raw)
            self.assertNotIn(fake_private_path, raw)
            self.assertNotIn(fake_bearer, raw)
            event = json.loads(raw)
            self.assertEqual(event["payload"]["safe"], "public measurement")
            self.assertEqual(event["payload"]["api_key"], "[REDACTED]")
            self.assertEqual(event["payload"]["delivery_path"], "<local-path-redacted>")
            self.assertEqual(event["payload"]["unknown"], "<unsupported:UnsafeRepr>")
            self.assertEqual(event["payload"]["token_count"], 42)
            self.assertEqual(
                event["payload"]["public_url"],
                "https://example.org/results/run-1",
            )

    def test_sequence_is_serialized_across_logger_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "evidence.jsonl"
            first = JsonlEvidenceLogger(path, "shared-run")
            second = JsonlEvidenceLogger(path, "shared-run")
            first.record("first", "floor", {})
            second.record("second", "delivery", {})
            first.record("third", "delivery", {})
            events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([item["sequence"] for item in events], [1, 2, 3])

    def test_existing_log_rejects_a_different_run_or_malformed_line(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "evidence.jsonl"
            JsonlEvidenceLogger(path, "first-run").record("first", "floor", {})
            with self.assertRaisesRegex(ValueError, "different run_id"):
                JsonlEvidenceLogger(path, "second-run")

            path.write_text("{not-json}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed"):
                JsonlEvidenceLogger(path, "first-run")

            path.write_text(
                json.dumps({"run_id": "first-run", "sequence": 1}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unterminated"):
                JsonlEvidenceLogger(path, "first-run")

            path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "timestamp": "2026-07-18T00:00:00+00:00",
                        "run_id": "first-run",
                        "sequence": True,
                        "event": "first",
                        "stage": "floor",
                        "payload": {},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "non-contiguous"):
                JsonlEvidenceLogger(path, "first-run")

    def test_only_one_loop_can_atomically_claim_an_empty_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "evidence.jsonl"
            loggers = [JsonlEvidenceLogger(path, "concurrent-run") for _ in range(2)]
            barrier = threading.Barrier(2)
            outcomes: list[str] = []

            def claim(logger):
                barrier.wait()
                try:
                    logger.begin_run({"worker": "synthetic"})
                except RuntimeError:
                    outcomes.append("rejected")
                else:
                    outcomes.append("claimed")

            threads = [threading.Thread(target=claim, args=(logger,)) for logger in loggers]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            self.assertCountEqual(outcomes, ["claimed", "rejected"])
            events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event"], "run_started")


if __name__ == "__main__":
    unittest.main()
