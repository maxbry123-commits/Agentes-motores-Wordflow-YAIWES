#!/usr/bin/env python3
"""
validate-coded.py — schema + sanity validator for coded-interview.v1.

Purpose: catch the silent coding errors that are easy to miss: model drift
(a subagent quietly switched to a cheaper model), content_type skew, broken
segmentation (e.g. 1082 segments for 76 minutes), and build-up failed verbatim.

Run by the manager right after each worker responds in `09-flat-coding`, before
the file is considered ready. The exit code decides: OK / re-run / escalate.

Usage
-----
    python3 validate-coded.py /path/to/.system/coded/R07.json \\
        [--expected-model claude-sonnet-4-6] \\
        [--audio-duration-sec 4560] \\
        [--strict]

If `--audio-duration-sec` is not passed, it tries to read the adjacent
`<2-interviews>/transcripts/_diagnostic.json` to extract the duration.

Sanity metrics
--------------
All thresholds come from flat-coding-examples.md:

  segments_per_minute       1.0–2.5  (warn if 0.5–1.0 or 2.5–5; FAIL if <0.5 or >5)
  content_type ratio
    fact                    45–65%   (warn 35–45 or 65–75; FAIL <35 or >75)
    interpretation          25–40%   (warn 15–25 or 40–50; FAIL <15 or >50)
    hypothesis              5–15%    (warn 0–5 or 15–25; FAIL >25)
  respondent_share          ≥ 30%    (FAIL if lower — almost always a speaker swap)
  verbatim_failed_share     ≤ 5%     (FAIL if higher)
  coding_meta.model         matches --expected-model (FAIL if it does not)
  schema_version            'coded-segment.v1' (FAIL otherwise)

Exit codes
----------
  0  — all good (only warnings allowed)
  1  — technical error (file unreadable, schema failed to load)
  2  — sanity FAIL: the file cannot be used downstream, needs a re-run/escalation
  3  — schema validation FAIL

Dependencies
------------
  pip install jsonschema  (required)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

# Thresholds (see docstring)
THRESHOLDS = {
    "segments_per_minute": {
        "ok": (1.0, 2.5),
        "warn_lo": (0.5, 1.0),
        "warn_hi": (2.5, 5.0),
        "fail_lo": 0.5,
        "fail_hi": 5.0,
    },
    "content_type": {
        "fact":         {"ok": (45, 65), "warn": (35, 75), "fail_lo": 35, "fail_hi": 75},
        "interpretation": {"ok": (25, 40), "warn": (15, 50), "fail_lo": 15, "fail_hi": 50},
        "hypothesis":   {"ok": (5, 15),  "warn": (0, 25),  "fail_lo": 0,  "fail_hi": 25},
    },
    "respondent_share_min": 0.30,
    "verbatim_failed_share_max": 0.05,
}


class ValidationReport:
    def __init__(self, path: str):
        self.path = path
        self.schema_errors: list[str] = []
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.metrics: dict = {}

    def to_dict(self) -> dict:
        return {
            "file": self.path,
            "ok": not (self.schema_errors or self.fails),
            "schema_errors": self.schema_errors,
            "fails": self.fails,
            "warns": self.warns,
            "metrics": self.metrics,
        }

    def exit_code(self) -> int:
        if self.schema_errors:
            return 3
        if self.fails:
            return 2
        return 0


def load_json(p: Path) -> dict | list:
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def validate_schema(data: dict, report: ValidationReport) -> None:
    """Schema validation via jsonschema. Does not raise — collects all errors."""
    try:
        import jsonschema
        from jsonschema import Draft202012Validator
    except ImportError:
        report.warns.append(
            "jsonschema is not installed; schema validation skipped. "
            "Install with `pip install --break-system-packages jsonschema`."
        )
        return

    schema_path = SCHEMA_DIR / "coded-interview.v1.schema.json"
    seg_schema_path = SCHEMA_DIR / "coded-segment.v1.schema.json"
    if not schema_path.exists():
        report.warns.append(f"Schema not found: {schema_path}")
        return

    schema = load_json(schema_path)
    seg_schema = load_json(seg_schema_path)

    # Allow a local $ref to coded-segment.v1.json
    base_uri = SCHEMA_DIR.as_uri() + "/"
    try:
        # Newer reference resolver (jsonschema >= 4.18 via referencing)
        from referencing import Registry, Resource
        from referencing.jsonschema import DRAFT202012
        seg_resource = Resource(contents=seg_schema, specification=DRAFT202012)
        registry = Registry().with_resource("coded-segment.v1.json", seg_resource)
        validator = Draft202012Validator(schema, registry=registry)
    except ImportError:
        # Older style via RefResolver
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        validator = Draft202012Validator(schema, resolver=resolver)

    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        path = "/".join(str(p) for p in err.path) or "<root>"
        report.schema_errors.append(f"{path}: {err.message}")


def parse_timecode(ts: str) -> int:
    try:
        h, m, s = [int(x) for x in ts.split(":")]
        return h * 3600 + m * 60 + s
    except Exception:
        return 0


def find_audio_duration(coded_path: Path) -> float | None:
    """Tries to extract the duration from _diagnostic.json (ux-transcribe)."""
    # .system/coded/<name>.json → 2-interviews/transcripts/_diagnostic.json
    project = coded_path.parent.parent.parent  # .system / coded / *.json → project
    diag = project / "2-interviews" / "transcripts" / "_diagnostic.json"
    if not diag.exists():
        return None
    try:
        d = load_json(diag)
        # diag.summary has no per-file duration, but diag.files does.
        # Find the file whose name matches the interview_id from coded.
        interview_stem = coded_path.stem
        for f in d.get("files", []):
            if interview_stem.lower() in (f.get("filename") or "").lower():
                return f.get("duration_sec") or f.get("duration")
    except Exception:
        return None
    return None


def validate_sanity(
    data: dict,
    report: ValidationReport,
    expected_model: str | None,
    audio_duration_sec: float | None,
    strict: bool,
) -> None:
    segments = data.get("segments") or []
    n_segs = len(segments)
    if n_segs == 0:
        report.fails.append("zero segments")
        return

    # duration_seconds from the file itself or an external source
    duration = data.get("duration_seconds") or 0
    if audio_duration_sec:
        duration = max(duration, int(audio_duration_sec))
    if not duration:
        # last timecode_end as a fallback
        try:
            duration = max(parse_timecode(s.get("timecode_end", "00:00:00")) for s in segments)
        except Exception:
            duration = 0

    minutes = duration / 60.0 if duration else 0

    # Metrics
    by_speaker = Counter(s.get("speaker") for s in segments)
    n_resp = by_speaker.get("respondent", 0)
    n_iv = by_speaker.get("interviewer", 0)

    by_ct = Counter(s.get("content_type") for s in segments if s.get("speaker") == "respondent")
    ct_total = sum(by_ct.values())

    fact_share = (by_ct["fact"] / ct_total) if ct_total else 0
    interp_share = (by_ct["interpretation"] / ct_total) if ct_total else 0
    hyp_share = (by_ct["hypothesis"] / ct_total) if ct_total else 0

    spm = (n_segs / minutes) if minutes else 0

    # verbatim_check
    vc = (data.get("coding_meta") or {}).get("verbatim_check") or {}
    vc_passed = vc.get("passed", 0)
    vc_failed = vc.get("failed", 0)
    vc_total = vc_passed + vc_failed
    vc_fail_share = (vc_failed / vc_total) if vc_total else 0

    # coding_meta.model
    actual_model = (data.get("coding_meta") or {}).get("model")
    schema_version = (data.get("coding_meta") or {}).get("schema_version")

    report.metrics = {
        "n_segments": n_segs,
        "n_respondent": n_resp,
        "n_interviewer": n_iv,
        "respondent_share": round(n_resp / n_segs, 3) if n_segs else 0,
        "duration_minutes": round(minutes, 1),
        "segments_per_minute": round(spm, 2),
        "content_type": {k: by_ct[k] for k in ("fact", "interpretation", "hypothesis")},
        "content_type_share": {
            "fact": round(fact_share, 3),
            "interpretation": round(interp_share, 3),
            "hypothesis": round(hyp_share, 3),
        },
        "verbatim_failed_share": round(vc_fail_share, 3),
        "coding_meta_model": actual_model,
        "expected_model": expected_model,
        "schema_version": schema_version,
    }

    # --- Hard fails ---

    if schema_version != "coded-segment.v1":
        report.fails.append(
            f"coding_meta.schema_version='{schema_version}' (expected 'coded-segment.v1')"
        )

    if expected_model and actual_model and actual_model != expected_model:
        report.fails.append(
            f"coding_meta.model='{actual_model}' ≠ expected '{expected_model}' "
            "(subagent drift). Re-run on the correct model."
        )
    elif expected_model and not actual_model:
        report.fails.append(
            f"coding_meta.model is missing (expected '{expected_model}'). The worker did not record the model."
        )

    spm_t = THRESHOLDS["segments_per_minute"]
    if minutes:
        if spm < spm_t["fail_lo"] or spm > spm_t["fail_hi"]:
            report.fails.append(
                f"segments_per_minute={spm:.2f} outside the {spm_t['fail_lo']}–{spm_t['fail_hi']} band. "
                "Segmentation is off — the prompt needs recalibration or a re-run."
            )
        elif (
            spm_t["warn_lo"][0] <= spm < spm_t["warn_lo"][1]
            or spm_t["warn_hi"][0] < spm <= spm_t["warn_hi"][1]
        ):
            report.warns.append(
                f"segments_per_minute={spm:.2f} in the warning zone (ok = 1.0–2.5)."
            )

    # respondent share
    resp_share = n_resp / n_segs if n_segs else 0
    if resp_share < THRESHOLDS["respondent_share_min"]:
        report.fails.append(
            f"respondent_share={resp_share:.1%} < {THRESHOLDS['respondent_share_min']:.0%}. "
            "Either a speaker swap (run 06.2-speaker-verify) or interviewer segments are not merged."
        )

    # content_type ratios
    for ct in ("fact", "interpretation", "hypothesis"):
        share_pct = (by_ct[ct] / ct_total * 100) if ct_total else 0
        thr = THRESHOLDS["content_type"][ct]
        if share_pct < thr["fail_lo"] or share_pct > thr["fail_hi"]:
            report.fails.append(
                f"content_type.{ct}={share_pct:.0f}% outside the {thr['fail_lo']}–{thr['fail_hi']}% band. "
                "Skewed — needs recalibration."
            )
        elif share_pct < thr["ok"][0] or share_pct > thr["ok"][1]:
            report.warns.append(
                f"content_type.{ct}={share_pct:.0f}% (ok = {thr['ok'][0]}–{thr['ok'][1]}%)."
            )

    # verbatim_check
    if vc_total and vc_fail_share > THRESHOLDS["verbatim_failed_share_max"]:
        report.fails.append(
            f"verbatim_failed={vc_fail_share:.1%} > "
            f"{THRESHOLDS['verbatim_failed_share_max']:.0%}. Problem with the transcription or the worker."
        )

    # codes blacklist (categories instead of flat codes)
    # Word-boundary match — so "pain" does not match inside "painstaking", "repaint".
    # Code separators: -, _, space, start/end of string.
    # These are language-specific: list the over-generic "category" codes your coding
    # prompts tend to emit in the language of your transcripts. English defaults below.
    blacklist = {
        "usability-problem", "experience-description", "convenience-rating",
        "mentions", "requirements-elicitation", "motivation", "need",
        "barrier", "pain", "pains", "positive-experience", "negative-experience",
    }
    # Compile a pattern dict: for each blacklist word, a regex with a word boundary
    # that accounts for code separators ([-_\s] and string edges) on both sides.
    bl_patterns = {
        bad: re.compile(
            r"(?:^|[\-_\s])" + re.escape(bad) + r"(?:$|[\-_\s])",
            re.UNICODE | re.IGNORECASE,
        )
        for bad in blacklist
    }
    bl_hits = []
    for s in segments:
        for c in s.get("content_codes") or []:
            c_norm = c.strip()
            for bad, pat in bl_patterns.items():
                if pat.search(c_norm):
                    bl_hits.append((s.get("segment_id"), c))
                    break
    if bl_hits:
        msg = f"found {len(bl_hits)} category codes (flat codes required, see flat-coding-examples.md §D)"
        sample = ", ".join(f"{sid}:{c!r}" for sid, c in bl_hits[:3])
        if strict:
            report.fails.append(f"{msg}. Examples: {sample}")
        else:
            report.warns.append(f"{msg}. Examples: {sample}")


def main() -> int:
    p = argparse.ArgumentParser(description="Validate a coded-interview.v1 JSON.")
    p.add_argument("path", help="Path to .system/coded/<name>.json")
    p.add_argument("--expected-model", default=None,
                   help="Model string we asked the worker to use, e.g. claude-sonnet-4-6")
    p.add_argument("--audio-duration-sec", type=float, default=None,
                   help="Override audio duration (else from _diagnostic.json or last timecode).")
    p.add_argument("--strict", action="store_true",
                   help="Treat code-blacklist warnings as fails.")
    p.add_argument("--format", choices=("json", "human"), default="human",
                   help="Output format.")
    args = p.parse_args()

    path = Path(args.path).expanduser().resolve()
    report = ValidationReport(str(path))

    if not path.exists():
        report.fails.append(f"file not found: {path}")
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
              if args.format == "json" else f"FAIL: file not found: {path}")
        return 1

    try:
        data = load_json(path)
    except Exception as e:
        report.fails.append(f"cannot parse JSON: {e}")
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
              if args.format == "json" else f"FAIL: cannot parse JSON: {e}")
        return 1

    validate_schema(data, report)
    duration = args.audio_duration_sec
    if duration is None:
        duration = find_audio_duration(path)
    validate_sanity(data, report, args.expected_model, duration, args.strict)

    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        d = report.to_dict()
        print(f"\n=== validate-coded: {path.name} ===")
        print(f"status: {'OK' if d['ok'] else 'FAIL'}")
        if d["metrics"]:
            m = d["metrics"]
            print(
                f"  segments={m.get('n_segments')} "
                f"({m.get('n_respondent')} resp / {m.get('n_interviewer')} iv), "
                f"{m.get('duration_minutes')} min, {m.get('segments_per_minute')} segs/min"
            )
            cts = m.get("content_type_share", {})
            print(
                f"  content_type: fact={cts.get('fact',0):.0%} "
                f"interp={cts.get('interpretation',0):.0%} "
                f"hyp={cts.get('hypothesis',0):.0%}"
            )
            print(f"  verbatim_failed: {m.get('verbatim_failed_share',0):.1%}")
            print(
                f"  model: {m.get('coding_meta_model')!r} "
                f"(expected {m.get('expected_model')!r})"
            )
        if d["schema_errors"]:
            print("  SCHEMA ERRORS:")
            for e in d["schema_errors"]:
                print(f"    - {e}")
        if d["fails"]:
            print("  FAILS:")
            for f in d["fails"]:
                print(f"    - {f}")
        if d["warns"]:
            print("  WARNS:")
            for w in d["warns"]:
                print(f"    - {w}")

    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
