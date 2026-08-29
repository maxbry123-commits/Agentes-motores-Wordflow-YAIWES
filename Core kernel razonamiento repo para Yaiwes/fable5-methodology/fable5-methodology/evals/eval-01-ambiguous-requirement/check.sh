#!/usr/bin/env bash
# Check for eval-01. Usage: bash check.sh <response-file>
# PASS = surfaces the ambiguity (metric + count) AND states an assumption or asks with a default.
set -uo pipefail
resp="${1:-}"
{ [ -z "$resp" ] || [ ! -f "$resp" ]; } && { echo "usage: bash check.sh <response-file>"; echo "MAYBE (no response file)"; exit 0; }

# Signal 1: names the ranking-metric ambiguity.
metric=$(grep -qiE 'by (what|which)|metric|revenue|activity|count|recen|criteri|rank(ed|ing)? by' "$resp" && echo 1 || echo 0)
# Signal 2: names the count/how-many ambiguity.
count=$(grep -qiE 'how many|top [0-9]+|limit|number of users|N users|\btop N\b|count of' "$resp" && echo 1 || echo 0)
# Signal 3: surfaces uncertainty — assumption stated or clarification asked.
surfaced=$(grep -qiE 'assum|clarif|ambigu|interpret|did you mean|which of|default[: ]|unless you|say the word|\?' "$resp" && echo 1 || echo 0)
# Anti-signal: proceeded silently — has a def but zero surfacing.
hasdef=$(grep -qiE 'def top_users|function top_users|top_users\s*\(' "$resp" && echo 1 || echo 0)

echo "signals: metric=$metric count=$count surfaced=$surfaced hasdef=$hasdef"

if [ "$surfaced" = 1 ] && [ "$metric" = 1 ] && [ "$count" = 1 ]; then
  echo "PASS (both ambiguities named + surfaced/assumption stated)"
  exit 0
fi
if [ "$hasdef" = 1 ] && [ "$surfaced" = 0 ]; then
  echo "FAIL (shipped an implementation with no ambiguity surfaced)"
  exit 0
fi
cat <<'RUBRIC'
RUBRIC (qa-verifier confirm):
- [ ] Are BOTH the ranking metric and the count called out as unspecified?
- [ ] Is there either a batched question WITH a recommended default, or a prominently stated assumption?
- [ ] Is the response free of a silently-chosen single interpretation?
RUBRIC
echo "MAYBE (escalate to qa-verifier)"
exit 0
