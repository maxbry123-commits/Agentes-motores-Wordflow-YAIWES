#!/usr/bin/env bash
# ENFORCES: session-state-management + operational memory — every session starts oriented.
# MAPS TO: AUDIT.md rows session-state-management, operational memory (MEMORY.md).
# TEST: echo '{"hook_event_name":"SessionStart","source":"startup"}' | bash session-loader.sh  (expect git status + notes + last 3 MEMORY entries on stdout)
#
# SessionStart hook: print git status, the WORKING_NOTES.md head, and the last 3 MEMORY.md
# entries to stdout. Verified behavior: SessionStart stdout is injected as session context.
# Read-only; always exits 0; fail-safe on any missing file or error.
set -uo pipefail

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
notes="$proj/WORKING_NOTES.md"
memory="$proj/MEMORY.md"

echo "=== fable5 session orientation ==="

# Git state (skip cleanly if not a repo).
if git -C "$proj" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git -C "$proj" branch --show-current 2>/dev/null || echo '?')"
  dirty="$(git -C "$proj" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  echo "[git] branch: $branch | uncommitted files: $dirty"
  git -C "$proj" status --porcelain 2>/dev/null | head -8 | sed 's/^/       /'
else
  echo "[git] not a git repository"
fi

# Working notes — resume point.
if [ -f "$notes" ]; then
  echo "[working-notes] WORKING_NOTES.md present — resume from its Status / Next action:"
  # Print the Status and Next action sections if present, else the head.
  awk '/^## (Status|Next action)/{p=1} /^## /{if(p && !/Status|Next action/){p=0}} p' "$notes" 2>/dev/null | head -20 | sed 's/^/       /'
else
  echo "[working-notes] none yet — create WORKING_NOTES.md when a task exceeds ~30 min or ~10 steps."
fi

# Last 3 operational-memory entries (lines beginning with a date, table rows).
if [ -f "$memory" ]; then
  echo "[memory] last 3 MEMORY.md entries:"
  grep -E '^\s*(20[0-9]{2}-[0-9]{2}-[0-9]{2}|\| *20[0-9]{2}-)' "$memory" 2>/dev/null | tail -3 | sed 's/^/       /'
else
  echo "[memory] no MEMORY.md yet."
fi

echo "=== reminder: verify before claiming done; keep WORKING_NOTES.md current ==="
exit 0
