#!/usr/bin/env python3
"""
detect_swaps.py — a heuristic detector of role confusion in ux-transcribe transcripts.

Context
-------
The Voxtral pipeline (Mistral) sometimes swaps the "Interviewer" and "Respondent"
roles in long interviews — especially in the second half of the recording and on long
summarizing turns. Across long transcripts, swaps show up in nearly every file (from a
couple to several dozen per interview). This script gives a fast heuristic signal of
whether an LLM re-attribute pass is needed.

Usage
-----
    python3 detect_swaps.py /path/to/2-interviews/transcripts/json/

The script reads all *.json files (ux-transcribe format — an array of
`{start,end,speaker,text}`) and, for each file, computes:
  * total_utterances
  * suspicious_interviewer (turns with interviewer markers, labeled as Respondent)
  * suspicious_respondent (long narratives, labeled as Interviewer)
  * suspicion_rate (share of suspicious turns)
  * needs_llm_pass (True if above threshold OR duration > 40 min)

Prints a JSON report to stdout. Exit code: 0 if no file needs an LLM pass,
2 if at least one does (a signal to the agent, not a script error).

Markers
-------
A heuristic, not a classifier — the list is deliberately incomplete and the LLM pass
always refines it.

NOTE: these markers are LANGUAGE-SPECIFIC. They match the phrasing and the role labels
in the transcript's own language. English defaults are shown below — replace them with
the equivalents for the language of your interviews.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Interviewer markers: command/question constructions, typical interview-guide phrasing.
# The regexes match words at the start of a turn, or standalone phrases.
# Language-specific — English defaults shown; swap for your interview language.
# ---------------------------------------------------------------------------
INTERVIEWER_MARKERS = [
    # Question constructions
    r"\btell me\b",
    r"\bcould you tell\b",
    r"\bcan you tell\b",
    r"\bshare with\b",
    r"\bexplain\b",
    r"\bdescribe\b",
    r"\bshow me\b",
    r"\bclarify\b",
    r"\bwalk me through\b",
    # Fillers and moderation phrases
    r"\blet's\b",
    r"\bto summarize\b",
    r"\bsumming up\b",
    r"\bto sum up\b",
    r"\bdid I understand (?:that )?correctly\b",
    r"\byou said\b",
    r"\byou mentioned\b",
    r"\byou noted\b",
    r"\blet's go back to\b",
    r"\bgoing back to\b",
    r"\bremember,? we\b",
    # Direct usability-scenario commands
    r"\bclick\b",
    r"\btap\b",
    r"\bpress\b",
    r"\bopen\b",
    r"\bclose\b",
    r"\bgo to\b",
    r"\btry to\b",
    r"\blook at\b",
    r"\bfind\b",
    r"\bselect\b",
    # Opening questions
    r"\band how\b",
    r"\band why\b",
    r"\band what\b",
    r"\bwhat if\b",
    r"\band tell me\b",
    # Acknowledging/prompting (standalone short turns)
    r"\bgot it\b\.?$",
    r"\bokay\b\.?$",
    r"\bok\b\.?$",
    r"\bthanks\b\.?$",
    r"\bright\b\.?$",
    r"\bmm-?hm\b\.?$",
    r"\buh-?huh\b\.?$",
    # Demographic openers from the guide
    r"\bhow old are you\b",
    r"\bwhere are you from\b",
    r"\bwhat do you do\b",
    r"\btell me about yourself\b",
    # Metacommunication
    r"\bI'll show\b",
    r"\blet me show\b",
    r"\bmoving on\b",
    r"\bnext question\b",
    r"\blast question\b",
    r"\bone more question\b",
    r"\bin conclusion\b",
]

# Respondent-narrative markers: personal pronouns + past-experience verbs.
# Weaker than the interviewer markers — narrative is possible from the interviewer in
# rare cases. Language-specific — English defaults shown.
RESPONDENT_MARKERS = [
    r"\bI (?:searched|looked|bought|rented|found|used|tried|opened|visited|saw|thought|decided|noticed)\b",
    r"\bI (?:had|have)\b",
    r"\bit (?:seemed|seems) to me\b",
    r"\b(?:I think|I feel|I like|I don't like)\b",
    r"\bwhen I\b",
    r"\bin my (?:case|experience)\b",
    r"\bpersonally,? I\b",
    r"\bI usually\b",
    r"\bmy experience\b",
]


INTERVIEWER_RE = re.compile("|".join(INTERVIEWER_MARKERS), re.IGNORECASE)
RESPONDENT_RE = re.compile("|".join(RESPONDENT_MARKERS), re.IGNORECASE)


# Normalize localized role labels. The transcriber may return "Interviewer", "Respondent",
# "Moderator", "Participant", or "Speaker 0/1" (on fallback) — map them to the canon.
# Language-specific — add the role labels your transcriber emits in its language.
ROLE_INTERVIEWER = {"interviewer", "moderator", "interviewer 1", "moderator 1"}
ROLE_RESPONDENT = {"respondent", "participant", "participant 1", "respondent 1"}


def normalize_role(role: str) -> str:
    """Map a localized role to the canon: 'interviewer' | 'respondent' | 'other'."""
    r = (role or "").strip().lower()
    if r in ROLE_INTERVIEWER:
        return "interviewer"
    if r in ROLE_RESPONDENT:
        return "respondent"
    return "other"


def analyse_file(json_path: Path) -> dict:
    """Compute swap metrics for a single transcript.

    Returns a structure:
        {
          "file": "...",
          "duration_sec": float,
          "total_utterances": int,
          "by_role": {"interviewer": N, "respondent": N, "other": N},
          "suspicious_interviewer": [{"idx": i, "ts": t, "text": ..., "markers": [...]}],
          "suspicious_respondent": [...],
          "suspicion_rate": float,
          "needs_llm_pass": bool,
          "reasons": [list of strings]
        }
    """
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"file": str(json_path), "error": f"Cannot read JSON: {e}"}

    if not isinstance(data, list):
        return {"file": str(json_path), "error": "Expected a JSON array of utterances"}

    by_role = {"interviewer": 0, "respondent": 0, "other": 0}
    suspicious_int = []   # turns labeled as Respondent but sounding like the interviewer
    suspicious_resp = []  # turns labeled as Interviewer but sounding like the respondent

    duration_sec = 0.0
    for i, utt in enumerate(data):
        if not isinstance(utt, dict):
            continue
        role_canon = normalize_role(utt.get("speaker", ""))
        by_role[role_canon] = by_role.get(role_canon, 0) + 1
        end = utt.get("end")
        if isinstance(end, (int, float)) and end > duration_sec:
            duration_sec = float(end)

        text = (utt.get("text") or "").strip()
        if not text:
            continue

        # Turns labeled as Respondent — look for interviewer markers in short turns.
        if role_canon == "respondent":
            markers = INTERVIEWER_RE.findall(text)
            # Heuristic: interviewer marker + a short turn (< 250 chars) — suspicious.
            # A long narrative with a single "Could you tell me" — not suspicious.
            if markers and len(text) < 250:
                suspicious_int.append({
                    "idx": i,
                    "ts": _fmt_ts(utt.get("start"), utt.get("end")),
                    "text": text[:200],
                    "markers": list({m.lower() for m in markers}),
                })

        # Turns labeled as Interviewer — look for long narratives.
        elif role_canon == "interviewer":
            # A long interviewer turn by itself is not suspicious (usability scenario, summarizing).
            # Suspicious — a long turn WITH narrative markers.
            if len(text) > 300:
                markers = RESPONDENT_RE.findall(text)
                if markers:
                    suspicious_resp.append({
                        "idx": i,
                        "ts": _fmt_ts(utt.get("start"), utt.get("end")),
                        "text": text[:200],
                        "markers": list({m.lower() for m in markers}),
                    })

    total = sum(by_role.values())
    susp_count = len(suspicious_int) + len(suspicious_resp)
    susp_rate = (susp_count / total) if total else 0.0

    reasons = []
    # LLM-pass triggers:
    if duration_sec > 40 * 60:
        reasons.append(f"duration {duration_sec/60:.1f} min > 40 min")
    if susp_count >= 3:
        reasons.append(f"{susp_count} suspicious utterances")
    if susp_rate >= 0.02:
        reasons.append(f"suspicion_rate {susp_rate:.1%} >= 2%")
    # Role skew — e.g. the respondent has <30% of turns — almost always a swap.
    if total and by_role.get("respondent", 0) / total < 0.30:
        reasons.append(
            f"role imbalance: respondent {by_role.get('respondent', 0)}/{total} < 30%"
        )

    needs_llm_pass = bool(reasons)

    return {
        "file": json_path.name,
        "duration_sec": round(duration_sec, 1),
        "total_utterances": total,
        "by_role": by_role,
        "suspicious_interviewer": suspicious_int,
        "suspicious_respondent": suspicious_resp,
        "suspicion_rate": round(susp_rate, 4),
        "needs_llm_pass": needs_llm_pass,
        "reasons": reasons,
    }


def _fmt_ts(start: float | None, end: float | None) -> str:
    def _f(s):
        if s is None:
            return "??"
        s = int(s)
        h, rem = divmod(s, 3600)
        m, s = divmod(rem, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
    return f"[{_f(start)} – {_f(end)}]"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Detect speaker-attribution swaps in ux-transcribe JSON files."
    )
    p.add_argument(
        "json_dir",
        help="Path to <folder>/transcripts/json/ directory (or a single .json file).",
    )
    p.add_argument(
        "--max-examples",
        type=int,
        default=5,
        help="Max suspicious utterances of each kind to include in the report (default 5).",
    )
    args = p.parse_args()

    target = Path(args.json_dir).expanduser().resolve()
    if not target.exists():
        print(f"Path does not exist: {target}", file=sys.stderr)
        return 1

    if target.is_file():
        files = [target]
    else:
        files = sorted(target.glob("*.json"))
        # _diagnostic.json lives in the parent folder, not in json/, but just in case:
        files = [f for f in files if f.name != "_diagnostic.json"]

    if not files:
        print(f"No .json files found in {target}", file=sys.stderr)
        return 1

    results = []
    needs_pass = False
    for f in files:
        r = analyse_file(f)
        # Truncate long example lists
        for k in ("suspicious_interviewer", "suspicious_respondent"):
            if isinstance(r.get(k), list):
                r[k] = r[k][: args.max_examples]
        results.append(r)
        if r.get("needs_llm_pass"):
            needs_pass = True

    report = {
        "tool": "detect_swaps",
        "version": "1.0",
        "input": str(target),
        "files_total": len(results),
        "files_needing_llm_pass": sum(1 for r in results if r.get("needs_llm_pass")),
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if needs_pass else 0


if __name__ == "__main__":
    sys.exit(main())
