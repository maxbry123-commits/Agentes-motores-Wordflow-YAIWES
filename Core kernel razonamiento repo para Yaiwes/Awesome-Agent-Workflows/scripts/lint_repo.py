#!/usr/bin/env python3
"""Small repository hygiene check for Awesome Agent Workflows."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDERS = ("TBD", "TODO", "Lorem ipsum", "<todo>")
REQUIRED = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "docs/WORKFLOW-CATALOG.md",
    "docs/curation-policy.md",
    "docs/launch/GROWTH-PLAN.md",
    "templates/agent-brief.md",
    "templates/workflow-card.md",
]

LOCAL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_catalog() -> None:
    data = json.loads((ROOT / "agent-workflows.json").read_text())
    if len(data) < 10:
        fail("expected at least 10 workflows in agent-workflows.json")
    ids = [item["id"] for item in data]
    if len(ids) != len(set(ids)):
        fail("workflow ids must be unique")
    for item in data:
        path = ROOT / item["path"]
        if not path.exists():
            fail(f"workflow path missing: {item['path']}")


def check_placeholders() -> None:
    allow_angle_templates = {"templates/agent-brief.md", "templates/workflow-card.md"}
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(errors="replace")
        for marker in PLACEHOLDERS:
            if marker in text:
                fail(f"placeholder marker {marker!r} found in {rel}")
        if rel not in allow_angle_templates and re.search(r"<[^>\n]{3,}>", text):
            fail(f"angle-bracket placeholder found in {rel}")


def check_local_links() -> None:
    for path in ROOT.rglob("*.md"):
        text = path.read_text(errors="replace")
        for raw in LOCAL_LINK.findall(text):
            target = raw.split("#", 1)[0].strip()
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            if not str(candidate).startswith(str(ROOT)):
                fail(f"local link escapes repo in {path.relative_to(ROOT)}: {raw}")
            if not candidate.exists():
                fail(f"broken local link in {path.relative_to(ROOT)}: {raw}")


def main() -> None:
    check_required_files()
    check_catalog()
    check_placeholders()
    check_local_links()
    print("repo hygiene check passed")


if __name__ == "__main__":
    main()
