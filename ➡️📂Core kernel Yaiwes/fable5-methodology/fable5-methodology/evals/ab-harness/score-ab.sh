#!/usr/bin/env bash
# Score a methodology-vs-baseline A/B run. See README.md for the run layout.
# Usage: bash score-ab.sh <run-dir>
#   <run-dir>/baseline/     eval-0N.txt (01-03) and eval-0N/ dirs (04-05)
#   <run-dir>/methodology/  same layout
#   <run-dir>/tokens.tsv    rows: "eval-id <TAB> baseline_tokens <TAB> methodology_tokens"
# Prints a per-eval WIN/LOSS/TIE table net of tokens, then a net summary.
# Exit 0 if net quality gain (WINS>LOSSES) with no unadjudicated blockers, else 1.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; evals_root="$(cd "$here/.." && pwd)"
run="${1:-}"
[ -z "$run" ] || [ ! -d "$run" ] && { echo "usage: bash score-ab.sh <run-dir>"; exit 2; }

tokfile="$run/tokens.tsv"
tok() { # tok <eval-id> <col: 2=baseline 3=methodology>
  [ -f "$tokfile" ] && awk -F'\t' -v e="$1" -v c="$2" '$1==e{print $c}' "$tokfile" | head -1
}

# eval-id : check-input-kind (file|dir) : response basename
EVALS="eval-01-ambiguous-requirement:file:eval-01.txt
eval-02-version-mismatch:file:eval-02.txt
eval-03-multi-requirement:file:eval-03.txt
eval-04-regression-trap:dir:eval-04
eval-05-scope-creep:dir:eval-05"

verdict_of() { # verdict_of <eval-dir> <kind> <arm-dir> <basename>
  local ed="$1" kind="$2" arm="$3" base="$4" path out
  if [ "$kind" = file ]; then path="$arm/$base"; [ -f "$path" ] || { echo "SKIP"; return; }
  else path="$arm/$base"; [ -d "$path" ] || { echo "SKIP"; return; }; fi
  out="$(bash "$ed/check.sh" "$path" 2>&1)" || true
  printf '%s\n' "$out" | grep -oE '^(PASS|FAIL|MAYBE)' | tail -1 | grep . || echo "MAYBE"
}

wins=0; losses=0; ties=0; maybe=0; skip=0; over_total=0
printf '%-32s %-9s %-11s %8s %8s  %s\n' "EVAL" "BASELINE" "METHOD" "b.tok" "m.tok" "OUTCOME"
printf -- '%.0s-' {1..92}; echo
while IFS=: read -r id kind base; do
  [ -z "$id" ] && continue
  bd="$run/baseline"; md="$run/methodology"
  bv="$(verdict_of "$evals_root/$id" "$kind" "$bd" "$base")"
  mv="$(verdict_of "$evals_root/$id" "$kind" "$md" "$base")"
  bt="$(tok "$id" 2)"; mt="$(tok "$id" 3)"
  outcome="TIE"
  if [ "$bv" = SKIP ] || [ "$mv" = SKIP ]; then outcome="SKIPPED"; skip=$((skip+1))
  elif [ "$bv" = MAYBE ] || [ "$mv" = MAYBE ]; then outcome="MAYBE(adjudicate)"; maybe=$((maybe+1))
  elif [ "$mv" = PASS ] && [ "$bv" = FAIL ]; then outcome="WIN"; wins=$((wins+1))
  elif [ "$mv" = FAIL ] && [ "$bv" = PASS ]; then outcome="LOSS"; losses=$((losses+1))
  else ties=$((ties+1)); fi
  if [ -n "${bt:-}" ] && [ -n "${mt:-}" ]; then over=$((mt-bt)); over_total=$((over_total+over)); fi
  printf '%-32s %-9s %-11s %8s %8s  %s\n' "$id" "$bv" "$mv" "${bt:-?}" "${mt:-?}" "$outcome"
done <<< "$EVALS"

echo
echo "NET: wins=$wins losses=$losses ties=$ties  |  maybe=$maybe skipped=$skip  |  token overhead(total)=${over_total}"
echo "Quality net (wins-losses): $((wins-losses))"
[ "$maybe" -gt 0 ] && echo "  → $maybe MAYBE(s) need qa-verifier/human adjudication before this A/B is complete."
[ "$skip" -gt 0 ] && echo "  → $skip SKIPPED — provide both arms' outputs and re-run."
echo "Verdict rule (§17.4): justified only if (wins>losses) AND the token overhead on Trivial/Small tasks is acceptable to you."
{ [ "$((wins-losses))" -gt 0 ] && [ "$maybe" -eq 0 ] && [ "$skip" -eq 0 ]; } && exit 0 || exit 1
