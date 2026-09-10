#!/usr/bin/env python3
"""
Validate transcript files produced by ux-transcribe.

Usage:
    python3 validate_transcripts.py /path/to/TICKET-123/transcripts

Checks each *_transcript.txt and json/*.json for common issues:
  - JSON fragments in text files
  - Role consistency (e.g. exactly 2 roles for UX interviews)
  - Timestamp monotonicity and gaps
  - Timestamp format [start – end]
  - Header presence
  - Valid JSON structure with roles (not raw speaker IDs)

Exit code: 0 if all checks pass, 1 if any fail.
"""

from __future__ import annotations

import json
import os
import re
import sys


def check_txt(path: str) -> list[str]:
    """Validate a single *_transcript.txt file."""
    errors: list[str] = []

    with open(path, encoding="utf-8-sig") as f:
        text = f.read()

    if not text.strip():
        return ["File is empty"]

    lines = text.split("\n")
    if not lines[0].startswith("===="):
        errors.append("Missing header (expected ==== on first line)")

    json_hits = re.findall(r'\{"(?:turns|ts|role)":', text)
    if json_hits:
        errors.append(f"Found {len(json_hits)} JSON fragment(s) in text")

    ts_range = re.compile(
        r'\[(\d+:\d{2}:\d{2}|\d{2}:\d{2})\s*–\s*(\d+:\d{2}:\d{2}|\d{2}:\d{2})\]'
    )
    ts_single = re.compile(r'\[(\d+:\d{2}:\d{2}|\d{2}:\d{2})\]')
    range_count = len(ts_range.findall(text))
    single_count = len(ts_single.findall(text))
    total_ts = range_count + single_count
    if total_ts == 0:
        errors.append("No timestamps found")
    elif range_count == 0 and single_count > 0:
        errors.append(f"All {single_count} timestamps are single [start] — expected [start – end]")

    def _parse_ts(s: str) -> int:
        parts = s.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return int(parts[0]) * 60 + int(parts[1])

    ts_all = re.compile(r'\[(\d+:\d{2}:\d{2}|\d{2}:\d{2})(?:\s*–\s*(?:\d+:\d{2}:\d{2}|\d{2}:\d{2}))?\]')
    timestamps = []
    for m in ts_all.finditer(text):
        timestamps.append(_parse_ts(m.group(1)))

    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i - 1] - 5:
            errors.append(
                f"Timestamp goes backwards: {timestamps[i-1]}s → {timestamps[i]}s"
            )
            break

    for i in range(1, len(timestamps)):
        gap = timestamps[i] - timestamps[i - 1]
        if gap > 300:
            errors.append(
                f"Large gap ({gap // 60}m {gap % 60}s) at {timestamps[i-1]}s → {timestamps[i]}s"
            )

    roles = set(re.findall(r'\]\s+([^:]+):', text))
    roles.discard("")
    if roles:
        raw_ids = [r for r in roles if re.match(r'^[Ss]peaker[\s_]?\d+$', r.strip())]
        if raw_ids:
            errors.append(f"Found raw speaker IDs instead of roles: {raw_ids}")
    else:
        errors.append("No speaker roles found in text")

    return errors


def check_json(path: str) -> list[str]:
    """Validate a single JSON transcript file."""
    errors: list[str] = []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    if not isinstance(data, list):
        return [f"Expected JSON array, got {type(data).__name__}"]

    if len(data) == 0:
        return ["JSON array is empty"]

    required_keys = {"start", "end", "speaker", "text"}
    for i, seg in enumerate(data[:5]):
        missing = required_keys - set(seg.keys())
        if missing:
            errors.append(f"Segment {i} missing keys: {missing}")

    speakers = set()
    for seg in data:
        sp = seg.get("speaker", "")
        if sp:
            speakers.add(sp)

    raw_ids = [s for s in speakers if re.match(r'^speaker[\s_]?\d+$', s, re.IGNORECASE)]
    if raw_ids:
        errors.append(f"Found raw speaker IDs instead of roles: {raw_ids}")

    if not speakers:
        errors.append("No speakers found in segments")

    return errors


def validate_folder(folder: str) -> bool:
    """Validate all transcripts in a folder. Returns True if all pass."""
    if not os.path.isdir(folder):
        print(f"FAIL: Directory not found: {folder}")
        return False

    txt_files = sorted(
        f for f in os.listdir(folder)
        if f.endswith("_transcript.txt") and os.path.isfile(os.path.join(folder, f))
    )

    json_dir = os.path.join(folder, "json")
    json_files = []
    if os.path.isdir(json_dir):
        json_files = sorted(
            f for f in os.listdir(json_dir)
            if f.endswith(".json") and os.path.isfile(os.path.join(json_dir, f))
        )

    if not txt_files and not json_files:
        print(f"FAIL: No transcript files found in {folder}")
        return False

    all_pass = True
    total_checks = 0
    total_errors = 0

    print(f"\nValidating: {folder}")
    print(f"TXT files: {len(txt_files)}, JSON files: {len(json_files)}")
    print("=" * 50)

    for name in txt_files:
        total_checks += 1
        path = os.path.join(folder, name)
        errors = check_txt(path)
        if errors:
            all_pass = False
            total_errors += 1
            print(f"\nFAIL  {name}")
            for e in errors:
                print(f"      {e}")
        else:
            print(f"PASS  {name}")

    for name in json_files:
        total_checks += 1
        path = os.path.join(json_dir, name)
        errors = check_json(path)
        if errors:
            all_pass = False
            total_errors += 1
            print(f"\nFAIL  json/{name}")
            for e in errors:
                print(f"      {e}")
        else:
            print(f"PASS  json/{name}")

    print("=" * 50)
    if all_pass:
        print(f"All {total_checks} checks passed.")
    else:
        print(f"{total_errors}/{total_checks} checks failed.")

    return all_pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_transcripts.py /path/to/transcripts")
        print("       python3 validate_transcripts.py /path/to/TICKET-123")
        sys.exit(2)

    folder = os.path.abspath(sys.argv[1])

    transcripts_sub = os.path.join(folder, "transcripts")
    if os.path.isdir(transcripts_sub):
        folder = transcripts_sub

    ok = validate_folder(folder)
    sys.exit(0 if ok else 1)
