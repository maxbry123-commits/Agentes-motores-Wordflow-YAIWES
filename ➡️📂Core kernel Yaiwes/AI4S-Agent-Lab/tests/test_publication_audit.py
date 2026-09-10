import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_publication import MAX_FILE_BYTES, verify_repository


class PublicationAuditTests(unittest.TestCase):
    def _write_valid_trace(self, root: Path) -> Path:
        trace = root / "evidence" / "reconstructed_traces" / "trace.jsonl"
        trace.parent.mkdir(parents=True)
        events = [
            {
                "trace_id": "public-reconstruction",
                "sequence": sequence,
                "reconstructed": True,
                "not_original_log": True,
            }
            for sequence in range(2)
        ]
        trace.write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )
        return trace

    def test_valid_minimal_candidate_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_valid_trace(root)
            (root / "README.md").write_text(
                "[Trace](evidence/reconstructed_traces/trace.jsonl)\n"
            )

            result = verify_repository(root)

            self.assertTrue(result.ok, result.issues)
            self.assertEqual(result.trace_count, 1)
            self.assertEqual(result.trace_event_count, 2)

    def test_publication_boundaries_reject_files_and_sensitive_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_valid_trace(root)
            (root / "model.ckpt").write_bytes(b"not-a-real-model")
            (root / "oversized.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
            (root / "legacy.txt").write_text("SERVER_" + "9876\n")
            (root / "opaque").write_bytes(b"\xff\xfe")
            (root / "nul.txt").write_bytes(b"public\x00hidden")
            (root / "target.txt").write_text("target\n")
            (root / "link.txt").symlink_to(root / "target.txt")

            result = verify_repository(root)
            joined = "\n".join(result.issues)

            self.assertFalse(result.ok)
            self.assertIn("prohibited model/data/key/archive suffix", joined)
            self.assertIn("file is 1048577 bytes", joined)
            self.assertIn("server-style environment identifier", joined)
            self.assertEqual(joined.count("non-UTF-8 or NUL-containing"), 2)
            self.assertIn("symbolic links are not allowed", joined)

    def test_broken_markdown_and_invalid_trace_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trace = self._write_valid_trace(root)
            events = [
                {
                    "trace_id": "public-reconstruction",
                    "sequence": 0,
                    "reconstructed": True,
                    "not_original_log": True,
                },
                {
                    "trace_id": "public-reconstruction",
                    "sequence": 2,
                    "reconstructed": False,
                    "not_original_log": False,
                },
            ]
            trace.write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )
            (root / "README.md").write_text("[missing](docs/missing.md)\n")

            result = verify_repository(root)
            joined = "\n".join(result.issues)

            self.assertFalse(result.ok)
            self.assertIn("broken relative link", joined)
            self.assertIn("sequence must be 1", joined)
            self.assertIn("reconstructed must be true", joined)
            self.assertIn("not_original_log must be true", joined)


if __name__ == "__main__":
    unittest.main()
