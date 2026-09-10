"""Compatibility package for MolClaw imports.

The source tree is vendored under `evaluation/Tools/molbench`, while upstream
runner modules import `MolClaw.*`. Expose the parent directory as the MolClaw
package path so those imports continue to resolve without renaming the bench.
"""
from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[1])]
