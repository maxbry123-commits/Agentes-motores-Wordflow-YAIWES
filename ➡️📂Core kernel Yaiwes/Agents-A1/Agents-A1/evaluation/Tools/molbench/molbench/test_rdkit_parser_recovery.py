"""Smoke tests for RDKit_bench answer parser recovery.

Run with:
  python -m molbench.test_rdkit_parser_recovery
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_PARENT = PROJECT_ROOT.parent
for path in (str(WORKSPACE_PARENT), str(PROJECT_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from molclaw_run.data_loader.bench_loaders import RdkitBenchLoader


def _sample(query: str) -> dict[str, str]:
    return {"query": query, "gt": "CCO", "meta": ""}


def _query() -> str:
    return """You are a cheminformatics assistant.

Task:
From the following SMILES list, output ALL molecules that satisfy ALL constraints below.

SMILES:
CCO
CCN
CCC

Constraints:
1) Dummy constraint.

Output format:
Print each satisfying SMILES on its own line, and nothing else.
"""


def _entry(raw_text: str, query: str | None = None) -> dict:
    loader = RdkitBenchLoader()
    result = {"action_history": [{"finish": raw_text}]}
    parsed = loader.parse_agent_result(result, "rdkit_bench")
    return loader.build_pred_entry(_sample(query or _query()), parsed, raw_text, "rdkit_bench")


def test_recovers_opd_closing_tag_as_opening() -> None:
    raw_text = """
<finish>Filtered 1 molecule.</answer>
CCO
</answer></finish>
"""
    entry = _entry(raw_text)
    assert entry["json_results"]["output"] == "CCO"


def test_preserves_normal_answer() -> None:
    raw_text = """
<finish>Filtered molecules.<answer>CCN</answer></finish>
<finish>Filtered 1 molecule.</answer>
CCO
</answer></finish>
"""
    entry = _entry(raw_text)
    assert entry["json_results"]["output"] == "CCN"


def test_refuses_non_candidate_recovery() -> None:
    raw_text = """
<finish>Filtered 1 molecule.</answer>
NONSENSE
</answer></finish>
"""
    entry = _entry(raw_text)
    assert entry["json_results"]["output"] == ""


def test_refuses_conflicting_recovered_blocks() -> None:
    raw_text = """
<finish>First result.</answer>
CCO
</answer></finish>
<finish>Second result.</answer>
CCN
</answer></finish>
"""
    entry = _entry(raw_text)
    assert entry["json_results"]["output"] == ""


if __name__ == "__main__":
    test_recovers_opd_closing_tag_as_opening()
    test_preserves_normal_answer()
    test_refuses_non_candidate_recovery()
    test_refuses_conflicting_recovered_blocks()
    print("RDKit_bench parser recovery smoke tests passed")
