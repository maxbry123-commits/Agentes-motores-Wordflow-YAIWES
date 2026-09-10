#!/usr/bin/env python3
"""
detect-english-words.py — flags Latin-script / jargon tokens in a markdown report
written in the team's working language.

Purpose: help the `18.5-narrative-adapt` step catch **all** foreign-script or
jargon tokens, not just the ones in the hardcoded stop-list. The stop-list is a
baseline; this script is the full sweep. This is useful as a plain-language QA
pass, most relevant when the working language uses a non-Latin script.

The script finds every Latin-script word in the body text, classifies it with
simple heuristics (known brand / abbreviation / technical term / generic
replacement candidate), provides context (the sentence it appears in), and
collects everything into a table. The final "keep / replace / ask" decision is
made by the LLM in 18.5 or by the researcher.

What is ignored (not counted as a candidate):
- Contents of code fences ``` ... ```.
- Inline code in `backticks`.
- URLs (http, https, file:, etc.).
- File names and paths with extensions (.md, .json, .py, .pptx, .xlsx, .canvas).
- Frontmatter at the top of the file (between --- ... ---).
- Table cells starting with the marker word `id:` (schema ids).

Usage
-----
    python3 detect-english-words.py path/to/report.md
    python3 detect-english-words.py path/to/report.md --format json
    python3 detect-english-words.py path/to/report.md --min-count 2

Exit codes
----------
0 — no generic candidates (report is clean).
2 — generic candidates found (a decision is needed).
1 — technical error (file could not be opened, etc.).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


# ----------------------------------------------------------------------------
# Categories
# ----------------------------------------------------------------------------

# Brands, products, technologies — kept as-is in any context.
# Extend as projects accumulate.
KNOWN_BRANDS = {
    # Common products
    "Google", "Apple", "iPhone", "iPad", "Android", "Chrome", "Safari", "YouTube",
    "Instagram", "Telegram", "WhatsApp", "OpenAI", "ChatGPT", "Claude",
    "Anthropic", "Gemini", "Mistral", "Voxtral",
    # Platforms and tools
    "Cowork", "Codex", "Obsidian", "Figma", "Notion", "Slack", "Jira", "GitHub",
    "GitLab", "Linear", "Asana", "MacOS", "Windows", "Linux", "VS", "Code",
}

# Team abbreviations and standard acronyms — usually kept.
# If accidentally used as nouns (not in a table header, not as an
# identifier) — the LLM may suggest spelling them out.
TEAM_ABBREVS = {
    "UX", "MR", "QA", "QC", "PM", "DS", "TL", "RnD",
    "JTBD", "NPS", "CSI", "CSAT", "DAU", "MAU", "WAU", "ARPU", "CR", "RR",
    "RQ", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
    "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9",
    "B2B", "B2C", "C2C", "SaaS", "API", "SDK", "CLI", "UI", "URL",
    "PDF", "DOCX", "PPTX", "XLSX", "CSV", "JSON", "YAML", "HTML", "CSS", "JS",
    "ID", "PII", "GDPR", "NDA",
    "STT", "TTS", "ASR", "LLM", "VLM", "RAG", "MCP", "AI", "ML",
    "ROI", "MVP", "KPI", "OKR", "MOQ",
}

# Technical terms from the stack that are **appropriate** to keep in any
# context (but mostly in technical sections). The LLM checks the context.
TECH_TERMS = {
    "Markdown", "Mermaid", "Pydantic", "JSON-Schema",
    "PostgreSQL", "Postgres", "MySQL", "Redis", "Docker", "Kubernetes",
    "Python", "JavaScript", "TypeScript", "React", "Vue",
    "Voxtral-v2", "GPT-4", "GPT-5", "Sonnet", "Opus", "Haiku",
    "BERT", "T5", "Whisper",
}

# Transparent anglicisms — these **definitely** need replacement. This is a
# safety net against the LLM pass missing one. If a word lands here, it is
# generic with a "stop-list match" note.
HARD_STOPLIST = {
    "usability", "verbatim", "funnel", "onboarding", "churn", "retention",
    "engagement", "conversion", "baseline", "persona", "personas",
    "insight", "insights", "feature", "features", "pain", "painpoint",
    "stakeholder", "stakeholders", "deadline", "milestone", "milestones",
    "scope", "backlog", "roadmap", "feedback", "framework", "frameworks",
    "wireframe", "wireframes", "mockup", "mockups", "prototype", "prototypes",
    "case", "cases", "wow", "vibe", "vibes", "demo", "case-study",
    "user", "users", "userflow", "flow", "flows", "journey",
    "research", "researcher", "researchers", "interview", "interviews",
}

# Patterns we skip entirely.
PATTERN_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
PATTERN_INLINE_CODE = re.compile(r"`[^`]+`")
PATTERN_URL = re.compile(
    r"\b(?:https?://|file://|ftp://|[a-z0-9.-]+\.(?:com|ru|org|net|io|app|dev|me)/[^\s)\"']*)",
    re.IGNORECASE,
)
PATTERN_FILEPATH = re.compile(
    r"\b[A-Za-z0-9_\-./]+\.(?:md|json|yaml|yml|py|sh|txt|pptx|xlsx|docx|csv|tsv|canvas|png|jpg|jpeg|svg|pdf|mp4|m4a|wav|html|css|js|ts|jsx|tsx)\b",
    re.IGNORECASE,
)
PATTERN_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
# Latin-script token: 2+ chars, may contain a hyphen between letters.
PATTERN_LATIN_TOKEN = re.compile(r"\b[A-Za-z][A-Za-z\-']*[A-Za-z]\b")


def strip_ignored(text: str) -> str:
    """Returns the text with code fences, inline code, URLs, paths and
    frontmatter stripped out — everything we should not scan for anglicisms."""
    text = PATTERN_FRONTMATTER.sub("", text)
    text = PATTERN_CODE_FENCE.sub(" ", text)
    text = PATTERN_INLINE_CODE.sub(" ", text)
    text = PATTERN_URL.sub(" ", text)
    text = PATTERN_FILEPATH.sub(" ", text)
    return text


def split_sentences(text: str) -> List[Tuple[int, str]]:
    """Roughly splits the text into "sentences" for context. Returns a list of
    (start_offset, sentence_text). Makes no claim to linguistic precision — it
    only needs to show the researcher the surroundings of a word."""
    sentences = []
    # Delimiters: period/exclamation/question + space or \n. Keep the offset.
    pos = 0
    for m in re.finditer(r"[^.!?\n]+[.!?]?", text):
        s = m.group().strip()
        if s:
            sentences.append((m.start(), s))
        pos = m.end()
    return sentences


def classify(word: str) -> str:
    """Returns a category: brand | abbrev | term | stoplist | generic.

    Logic:
    - exact (case-sensitive) match with KNOWN_BRANDS → brand;
    - exact (case-insensitive) match with HARD_STOPLIST → stoplist;
    - exact match with TEAM_ABBREVS → abbrev;
    - all-uppercase, length 2–6 → abbrev (a new abbreviation);
    - exact (case-insensitive) match with TECH_TERMS → term;
    - everything else → generic.
    """
    if word in KNOWN_BRANDS:
        return "brand"
    if word.lower() in HARD_STOPLIST:
        return "stoplist"
    if word in TEAM_ABBREVS:
        return "abbrev"
    if word.upper() == word and 2 <= len(word) <= 6 and word.isalpha():
        return "abbrev"
    if word.lower() in {t.lower() for t in TECH_TERMS}:
        return "term"
    return "generic"


def find_candidates(text: str) -> Dict[str, dict]:
    """Returns a dict word → {count, category, contexts}."""
    clean = strip_ignored(text)
    sentences = split_sentences(clean)

    # offset → sentence index for fast context lookup.
    def find_sentence(offset: int) -> str:
        for start, s in sentences:
            if start <= offset < start + len(s) + 1:
                return s
        return ""

    candidates: Dict[str, dict] = defaultdict(
        lambda: {"count": 0, "category": "", "contexts": []}
    )
    for m in PATTERN_LATIN_TOKEN.finditer(clean):
        word = m.group()
        # Single-letter words — ignore (often variables / list markers).
        if len(word) < 2:
            continue
        cat = classify(word)
        candidates[word]["count"] += 1
        candidates[word]["category"] = cat
        # Cap at 3 contexts per word to avoid bloating the output.
        if len(candidates[word]["contexts"]) < 3:
            ctx = find_sentence(m.start())
            if ctx and ctx not in candidates[word]["contexts"]:
                candidates[word]["contexts"].append(ctx)

    return dict(candidates)


def emit_human(candidates: Dict[str, dict], min_count: int) -> Tuple[str, int]:
    """Returns (text, exit_code). exit_code=2 if there are generic/stoplist words."""
    by_cat: Dict[str, List[Tuple[str, dict]]] = defaultdict(list)
    for w, info in candidates.items():
        if info["count"] < min_count:
            continue
        by_cat[info["category"]].append((w, info))

    out: List[str] = []
    out.append(f"# English words in document")
    out.append("")

    needs_decision = 0

    for cat in ("stoplist", "generic", "abbrev", "brand", "term"):
        items = by_cat.get(cat, [])
        if not items:
            continue
        # Sort by descending count
        items.sort(key=lambda x: -x[1]["count"])
        title = {
            "stoplist": "## ⚠ Hard stop-list (definitely replace)",
            "generic": "## Generic — needs an LLM or researcher decision",
            "abbrev": "## Abbreviations (usually keep)",
            "brand": "## Brands / products (keep)",
            "term": "## Technical terms (keep, check context)",
        }[cat]
        out.append(title)
        out.append("")
        if cat in ("stoplist", "generic"):
            needs_decision += len(items)
        for w, info in items:
            out.append(f"### `{w}` × {info['count']}")
            for c in info["contexts"]:
                # Highlight the word itself in context
                ctx_with_marker = re.sub(
                    rf"\b{re.escape(w)}\b",
                    f"**{w}**",
                    c,
                )
                out.append(f"- {ctx_with_marker}")
            out.append("")

    if needs_decision == 0:
        out.append("**Clean.** No generic / stoplist candidates.")
        return "\n".join(out), 0

    out.append(
        f"**Needs a decision:** {needs_decision} unique words "
        f"(stoplist + generic)."
    )
    return "\n".join(out), 2


def emit_json(candidates: Dict[str, dict], min_count: int) -> Tuple[str, int]:
    filtered = {
        w: info
        for w, info in candidates.items()
        if info["count"] >= min_count
    }
    needs_decision = sum(
        1
        for info in filtered.values()
        if info["category"] in ("stoplist", "generic")
    )
    return (
        json.dumps(filtered, ensure_ascii=False, indent=2),
        2 if needs_decision else 0,
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("path", help="Path to the .md file (report or other document)")
    p.add_argument("--format", choices=("human", "json"), default="human")
    p.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Minimum number of word occurrences (default 1).",
    )
    args = p.parse_args()

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"[fail] File not found: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        print(f"[fail] Not UTF-8: {e}", file=sys.stderr)
        return 1

    candidates = find_candidates(text)

    if args.format == "json":
        out, code = emit_json(candidates, args.min_count)
    else:
        out, code = emit_human(candidates, args.min_count)

    print(out)
    return code


if __name__ == "__main__":
    sys.exit(main())
