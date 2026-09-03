import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai4s_agent_lab.__main__ import main


class CommandLineTests(unittest.TestCase):
    def test_cli_prints_json_after_delivering_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = io.StringIO()
            with patch.object(
                sys,
                "argv",
                [
                    "ai4s-agent-lab",
                    "--output-dir",
                    temporary_directory,
                    "--iterations",
                    "2",
                    "--run-id",
                    "cli-test",
                ],
            ), contextlib.redirect_stdout(output):
                self.assertEqual(main(), 0)

            result = json.loads(output.getvalue())
            self.assertEqual(result["run_id"], "cli-test")
            self.assertIsInstance(result["best_parameters"], dict)
            self.assertTrue((Path(temporary_directory) / "evidence.jsonl").is_file())
            self.assertTrue((Path(temporary_directory) / "best_model.json").is_file())


if __name__ == "__main__":
    unittest.main()
