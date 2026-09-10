#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BENCH_DIR="$TOOLS_DIR/vita"
PYTHON_BIN="${PYTHON_BIN:-python}"

export PYTHONPATH="$BENCH_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
cd "$BENCH_DIR"

if [[ $# -gt 0 ]]; then
  exec "$PYTHON_BIN" -m vita.cli "$@"
fi

DOMAIN="${VITA_DOMAIN:-delivery}"
MODEL_NAME="${VITA_MODEL:-${MODEL:-Agents-A1}}"
USER_MODEL_NAME="${VITA_USER_MODEL:-${USER_MODEL:-deepseek-v3.2}}"
EVALUATOR_MODEL_NAME="${VITA_EVALUATOR_MODEL:-${EVALUATOR_MODEL:-deepseek-v3.2}}"
NUM_TRIALS="${VITA_NUM_TRIALS:-1}"
NUM_TASKS="${VITA_NUM_TASKS:-1}"
MAX_CONCURRENCY="${VITA_MAX_CONCURRENCY:-1}"
MAX_STEPS="${VITA_MAX_STEPS:-300}"
LANGUAGE="${VITA_LANGUAGE:-english}"
SAVE_TO="${VITA_SAVE_TO:-tools_vita_${DOMAIN//,/plus}_${MODEL_NAME//[^A-Za-z0-9_.-]/_}.json}"
SKIP_EVALUATION="${VITA_SKIP_EVALUATION:-0}"
LOG_LEVEL="${VITA_LOG_LEVEL:-ERROR}"

cmd=("$PYTHON_BIN" -m vita.cli run
  --domain "$DOMAIN"
  --agent-llm "$MODEL_NAME"
  --user-llm "$USER_MODEL_NAME"
  --evaluator-llm "$EVALUATOR_MODEL_NAME"
  --num-trials "$NUM_TRIALS"
  --num-tasks "$NUM_TASKS"
  --max-steps "$MAX_STEPS"
  --max-concurrency "$MAX_CONCURRENCY"
  --log-level "$LOG_LEVEL"
  --language "$LANGUAGE"
  --save-to "$SAVE_TO")

if [[ "$SKIP_EVALUATION" == "1" ]]; then
  cmd+=(--skip-evaluation)
fi

exec "${cmd[@]}"
