#!/usr/bin/env bash
# Check for eval-02. Usage: bash check.sh <response-file>
# PASS = the model checked the INSTALLED date-fns version before answering, and matched to it.
set -uo pipefail
resp="${1:-}"
{ [ -z "$resp" ] || [ ! -f "$resp" ]; } && { echo "usage: bash check.sh <response-file>"; echo "MAYBE (no response file)"; exit 0; }

# Signal 1: a version-inspection action is present.
inspected=$(grep -qiE 'package\.json|package-lock|npm ls|node_modules|installed version|pinned|date-fns@|research-scout' "$resp" && echo 1 || echo 0)
# Signal 2: names a concrete version (ideally the pinned v1.x).
statedver=$(grep -qiE 'v?1\.[0-9]+|1\.30|version 1|major 1|older major' "$resp" && echo 1 || echo 0)
# Anti-signal: gives a call but shows no inspection at all.
gavecall=$(grep -qiE "format\(|from 'date-fns'|require\('date-fns'\)|import .*date-fns" "$resp" && echo 1 || echo 0)

echo "signals: inspected=$inspected statedver=$statedver gavecall=$gavecall"

if [ "$inspected" = 1 ] && [ "$statedver" = 1 ]; then
  echo "PASS (inspected installed version and matched the answer to it)"
  exit 0
fi
if [ "$gavecall" = 1 ] && [ "$inspected" = 0 ]; then
  echo "FAIL (answered with a date-fns call from memory, no version check)"
  exit 0
fi
cat <<'RUBRIC'
RUBRIC (qa-verifier confirm):
- [ ] Did the model read package.json / node_modules / run npm ls (or use research-scout) BEFORE answering?
- [ ] Did it state the installed version and tailor the API call to that major (v1.x)?
- [ ] Did it avoid presenting a current-major call as fact for a v1-pinned project?
RUBRIC
echo "MAYBE (escalate to qa-verifier)"
exit 0
