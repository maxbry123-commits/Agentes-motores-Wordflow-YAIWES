import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai4s_agent_lab.artifacts import AtomicArtifactWriter


class AtomicArtifactWriterTests(unittest.TestCase):
    def test_replace_failure_preserves_previous_artifact_and_cleans_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "artifact.json"
            destination.write_text('{"state":"previous"}\n', encoding="utf-8")

            with patch("ai4s_agent_lab.artifacts.os.replace", side_effect=OSError("synthetic")):
                with self.assertRaises(OSError):
                    AtomicArtifactWriter().write_json(destination, {"state": "candidate"})

            self.assertEqual(destination.read_text(encoding="utf-8"), '{"state":"previous"}\n')
            self.assertFalse(list(destination.parent.glob(".artifact.json.*.tmp")))

    def test_readback_verification_returns_a_stable_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "artifact.json"
            value = {"state": "verified", "score": 1.0}
            writer = AtomicArtifactWriter()
            writer.write_json(destination, value)
            first = writer.verify_json(destination, value)
            second = writer.verify_json(destination, value)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 64)

            destination.write_text('{"score":true,"state":"verified"}\n', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                writer.verify_json(destination, value)

            destination.write_text(
                '{"score":1.0,"score":1.0,"state":"verified"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                writer.verify_json(destination, value)


if __name__ == "__main__":
    unittest.main()
