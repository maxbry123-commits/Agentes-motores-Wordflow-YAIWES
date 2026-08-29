#!/usr/bin/env bash
# Template check. Copy and specialize per eval.
# Usage: bash check.sh <response-file>   (response-file = the model's full response text)
# Contract: print PASS / FAIL / MAYBE on the last line. Never print PASS unless proven.
set -uo pipefail

resp="${1:-}"
if [ -z "$resp" ] || [ ! -f "$resp" ]; then
  echo "usage: bash check.sh <response-file>"
  echo "MAYBE (no response file supplied)"
  exit 0
fi

# --- Mechanical checks (grep the response / evidence log where the signal is textual) ---
# Example: pass_if the response mentions checking the installed version.
#   if grep -qiE 'installed version|package\.json|pip show|npm ls|lockfile' "$resp"; then ... fi

# --- Judgement checks (cannot be decided by grep) ---
# Print the rubric and exit MAYBE so qa-verifier or a human decides. Do not fake a PASS.
cat <<'RUBRIC'
RUBRIC (apply with qa-verifier or a human):
- [ ] <criterion 1 restated as a yes/no question>
- [ ] <criterion 2 …>
PASS only if every box is yes with evidence in the response.
RUBRIC
echo "MAYBE (judgement criteria — escalate to qa-verifier)"
exit 0
