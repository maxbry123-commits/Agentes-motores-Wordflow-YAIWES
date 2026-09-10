#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BENCH_DIR="$TOOLS_DIR/mattools"
PYTHON_BIN="${PYTHON_BIN:-python}"

if [[ -z "${CLAUDE_BIN:-}" ]] && command -v claude >/dev/null 2>&1; then
  export CLAUDE_BIN="$(command -v claude)"
fi

cd "$BENCH_DIR"

if [[ "${1:-}" == "--parser-self-test" || "${1:-}" == "smoke" ]]; then
  exec "$PYTHON_BIN" src/claude_cli_test/build_agent.py --parser-self-test
fi

if [[ $# -gt 0 ]]; then
  exec bash src/claude_cli_test/launch_claude.sh "$@"
fi

MODEL_NAME="${MATTOOLS_MODEL:-${MODEL:-Agents-A1}}"
LIMIT="${MATTOOLS_LIMIT:-1}"
MAX_PROCESS="${MATTOOLS_MAX_PROCESS:-1}"
TIMEOUT="${MATTOOLS_TIMEOUT_SECONDS:-600}"
RUN_NAME="${MATTOOLS_RUN_NAME:-tools_mattools_${MODEL_NAME//[^A-Za-z0-9_.-]/_}}"
SKIP_EVAL="${MATTOOLS_SKIP_EVAL:-1}"

cmd=(bash src/claude_cli_test/launch_claude.sh
  --model "$MODEL_NAME"
  --run-name "$RUN_NAME"
  --limit "$LIMIT"
  --timeout "$TIMEOUT"
  --max-process "$MAX_PROCESS")

if [[ "$SKIP_EVAL" == "1" ]]; then
  cmd+=(--skip-eval)
fi

exec "${cmd[@]}"
