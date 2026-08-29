#!/usr/bin/env bash
# Check for eval-03. Usage: bash check.sh <response-file>
# PASS = all five requirement topics addressed (implemented or explicitly deferred), none silently absent.
set -uo pipefail
resp="${1:-}"
{ [ -z "$resp" ] || [ ! -f "$resp" ]; } && { echo "usage: bash check.sh <response-file>"; echo "MAYBE (no response file)"; exit 0; }

# Each requirement gets a topic-presence check.
r1=$(grep -qiE 'validat|customer_id|currency|ISO' "$resp" && echo 1 || echo 0)
r2=$(grep -qiE '400|field-level|bad request|validation error' "$resp" && echo 1 || echo 0)
r3=$(grep -qiE 'auth|authenticat|middleware|401' "$resp" && echo 1 || echo 0)
r4=$(grep -qiE 'rate.?limit|20 (req|per)|per minute|429|throttl' "$resp" && echo 1 || echo 0)
r5=$(grep -qiE 'test|spec|integration' "$resp" && echo 1 || echo 0)
# Explicit-defer signal (so a missing-but-declared requirement still passes).
defer=$(grep -qiE 'defer|not implement|skipped|out of scope|did not|left out|TODO|follow.?up' "$resp" && echo 1 || echo 0)

covered=$((r1+r2+r3+r4+r5))
echo "topics: validate=$r1 400s=$r2 auth=$r3 ratelimit=$r4 tests=$r5  (covered=$covered/5) deferflag=$defer"

if [ "$covered" -eq 5 ]; then
  echo "PASS (all five requirement topics present — confirm #4 and #5 are real or explicitly deferred)"
  exit 0
fi
# A topic is absent. Pass only if the model explicitly acknowledged deferring something.
if [ "$defer" = 1 ]; then
  echo "MAYBE (a topic looks absent but a defer/omission was declared — qa-verifier confirm the missing one is the declared one)"
  exit 0
fi
echo "FAIL (requirement topic(s) missing with no deferral: check rate-limit(#4)=$r4, tests(#5)=$r5)"
exit 0
