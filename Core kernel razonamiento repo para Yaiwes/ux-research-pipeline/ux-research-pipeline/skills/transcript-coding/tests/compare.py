"""Regression comparison for coded-transcript outputs.

Takes two CodedTranscript JSON files (current vs golden) and produces a structured diff
focused on what actually matters for coding quality:
  - Number of segments (must match)
  - Per-segment: quote (exact), subject_codes (set equality), content_type (exact),
    research_question_ids (set equality), hypothesis_support (same ids + directions).
  - interpretive_notes: soft compare — same length ± 50%, no exact match required.
  - Any new validation warnings.

The exit code is 0 if the outputs are "regression-compatible", non-zero otherwise.

Usage:
    python3 tests/compare.py <current.coded.json> <golden.coded.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Make scripts importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from schemas import CodedTranscript  # noqa: E402


def load_coded(path: Path) -> CodedTranscript:
    return CodedTranscript(**json.loads(path.read_text(encoding="utf-8")))


def compare(current: CodedTranscript, golden: CodedTranscript) -> tuple[int, list[str]]:
    issues: list[str] = []

    # Segments count
    if len(current.segments) != len(golden.segments):
        issues.append(
            f"Segment count changed: {len(golden.segments)} (golden) -> "
            f"{len(current.segments)} (current)"
        )

    # Pair by segment_id for robust comparison
    golden_by_id = {s.segment_id: s for s in golden.segments}
    for seg in current.segments:
        g = golden_by_id.get(seg.segment_id)
        if g is None:
            issues.append(f"  + new segment: {seg.segment_id}")
            continue

        if seg.quote != g.quote:
            issues.append(f"  {seg.segment_id}: quote changed")
        if seg.content_type != g.content_type:
            issues.append(
                f"  {seg.segment_id}: content_type {g.content_type!r} -> {seg.content_type!r}"
            )

        g_codes = set(c.lower() for c in g.subject_codes)
        c_codes = set(c.lower() for c in seg.subject_codes)
        if g_codes != c_codes:
            added = c_codes - g_codes
            removed = g_codes - c_codes
            if added:
                issues.append(f"  {seg.segment_id}: +codes {sorted(added)}")
            if removed:
                issues.append(f"  {seg.segment_id}: -codes {sorted(removed)}")

        g_rq = set(g.research_question_ids)
        c_rq = set(seg.research_question_ids)
        if g_rq != c_rq:
            issues.append(
                f"  {seg.segment_id}: research_question_ids {sorted(g_rq)} -> {sorted(c_rq)}"
            )

        g_hs = {(h.hypothesis_id, h.direction) for h in g.hypothesis_support}
        c_hs = {(h.hypothesis_id, h.direction) for h in seg.hypothesis_support}
        if g_hs != c_hs:
            issues.append(
                f"  {seg.segment_id}: hypothesis_support {sorted(g_hs)} -> {sorted(c_hs)}"
            )

        # Soft compare of interpretive_notes: flag only if either side is empty and the
        # other is not, or length changed by more than 2x.
        g_n = len((g.interpretive_notes or "").strip())
        c_n = len((seg.interpretive_notes or "").strip())
        if (g_n == 0) != (c_n == 0):
            issues.append(f"  {seg.segment_id}: interpretive_notes emptiness flipped")
        elif g_n > 0 and (c_n < g_n * 0.5 or c_n > g_n * 2.0):
            issues.append(f"  {seg.segment_id}: interpretive_notes length changed materially "
                          f"({g_n} -> {c_n})")

    missing = set(golden_by_id.keys()) - {s.segment_id for s in current.segments}
    for sid in sorted(missing):
        issues.append(f"  - missing segment: {sid}")

    # New validation warnings
    def warnings_count(t: CodedTranscript) -> int:
        return sum(len(s.meta.validation_warnings) for s in t.segments)
    g_w = warnings_count(golden)
    c_w = warnings_count(current)
    if c_w > g_w:
        issues.append(f"New validation warnings: {g_w} -> {c_w}")

    return (0 if not issues else 1), issues


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: compare.py <current.coded.json> <golden.coded.json>", file=sys.stderr)
        return 2
    current = load_coded(Path(sys.argv[1]))
    golden = load_coded(Path(sys.argv[2]))
    rc, issues = compare(current, golden)
    if rc == 0:
        print("✅ Regression-compatible.")
    else:
        print(f"❌ {len(issues)} differences from golden:")
        for it in issues:
            print(it)
    return rc


if __name__ == "__main__":
    sys.exit(main())
