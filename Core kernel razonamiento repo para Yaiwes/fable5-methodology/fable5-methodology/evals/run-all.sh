#!/usr/bin/env bash
# Eval suite runner. Usage:
#   bash run-all.sh <responses-dir>
# where <responses-dir> contains, per eval, the model-under-test's output:
#   eval-01.txt  eval-02.txt  eval-03.txt   (response text for prompt-based evals)
#   eval-04/     eval-05/                    (the model-edited fixture DIRS for fixture evals)
# Missing inputs are reported as SKIPPED, never silently passed.
# Exit code: 0 if no FAILs (MAYBEs still need qa-verifier review), 1 if any FAIL.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
resp="${1:-}"
[ -z "$resp" ] && { echo "usage: bash run-all.sh <responses-dir>   (see header for expected layout)"; exit 1; }

pass=0; fail=0; maybe=0; skip=0
declare -a rows

run_one() { # run_one <eval-dir> <arg> <label>
  local dir="$1" arg="$2" label="$3" out verdict
  if [ -z "$arg" ]; then
    rows+=("SKIPPED  $label (no input provided)"); skip=$((skip+1)); return
  fi
  out="$(bash "$dir/check.sh" "$arg" 2>&1)" || true
  verdict="$(printf '%s\n' "$out" | grep -oE '^(PASS|FAIL|MAYBE)' | tail -1)"
  case "$verdict" in
    PASS)  pass=$((pass+1));;
    FAIL)  fail=$((fail+1));;
    *)     verdict="MAYBE"; maybe=$((maybe+1));;
  esac
  rows+=("$verdict  $label")
  printf '=== %s ===\n%s\n\n' "$label" "$out"
}

# Prompt-based evals take a response FILE; fixture evals take the edited fixture DIR.
run_one "$here/eval-01-ambiguous-requirement" "$([ -f "$resp/eval-01.txt" ] && echo "$resp/eval-01.txt")" "eval-01-ambiguous-requirement"
run_one "$here/eval-02-version-mismatch"      "$([ -f "$resp/eval-02.txt" ] && echo "$resp/eval-02.txt")" "eval-02-version-mismatch"
run_one "$here/eval-03-multi-requirement"     "$([ -f "$resp/eval-03.txt" ] && echo "$resp/eval-03.txt")" "eval-03-multi-requirement"
run_one "$here/eval-04-regression-trap"       "$([ -d "$resp/eval-04" ] && echo "$resp/eval-04")"         "eval-04-regression-trap"
run_one "$here/eval-05-scope-creep"           "$([ -d "$resp/eval-05" ] && echo "$resp/eval-05")"         "eval-05-scope-creep"

echo "================= EVAL SUITE SUMMARY ================="
printf '  %s\n' "${rows[@]}"
echo "  ----"
echo "  PASS=$pass  FAIL=$fail  MAYBE=$maybe  SKIPPED=$skip"
[ "$maybe" -gt 0 ] && echo "  MAYBEs are NOT passes — hand each to qa-verifier with the printed rubric."
[ "$skip" -gt 0 ] && echo "  SKIPPEDs are NOT passes — provide the missing inputs and re-run."
[ "$fail" -eq 0 ] && exit 0 || exit 1
