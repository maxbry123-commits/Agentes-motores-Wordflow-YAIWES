#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BENCH_DIR="$TOOLS_DIR/tau2"
PYTHON_BIN="${PYTHON_BIN:-python}"

export PYTHONPATH="$BENCH_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
export TAU2_DATA_DIR="${TAU2_DATA_DIR:-$BENCH_DIR/data}"
cd "$BENCH_DIR"

if [[ $# -gt 0 ]]; then
  exec "$PYTHON_BIN" -m tau2.cli "$@"
fi

DOMAIN="${TAU2_DOMAIN:-airline}"
AGENT_LLM="${TAU2_AGENT_LLM:-${MODEL:-Agents-A1}}"
USER_LLM="${TAU2_USER_LLM:-${USER_MODEL:-deepseek-v3.2}}"
NUM_TRIALS="${TAU2_NUM_TRIALS:-1}"
NUM_TASKS="${TAU2_NUM_TASKS:-5}"
MAX_CONCURRENCY="${TAU2_MAX_CONCURRENCY:-1}"
TASK_SPLIT="${TAU2_TASK_SPLIT:-base}"
SAVE_TO="${TAU2_SAVE_TO:-tools_tau2_${DOMAIN}_${AGENT_LLM//[^A-Za-z0-9_.-]/_}}"
AGENT_LLM_ARGS="${TAU2_AGENT_LLM_ARGS:-}"
USER_LLM_ARGS="${TAU2_USER_LLM_ARGS:-}"

cmd=(
  "$PYTHON_BIN" -m tau2.cli run
  --domain "$DOMAIN" \
  --agent-llm "$AGENT_LLM" \
  --user-llm "$USER_LLM" \
  --num-trials "$NUM_TRIALS" \
  --num-tasks "$NUM_TASKS" \
  --max-concurrency "$MAX_CONCURRENCY" \
  --task-split-name "$TASK_SPLIT" \
  --save-to "$SAVE_TO"
)

if [[ -n "$AGENT_LLM_ARGS" ]]; then
  cmd+=(--agent-llm-args "$AGENT_LLM_ARGS")
fi

if [[ -n "$USER_LLM_ARGS" ]]; then
  cmd+=(--user-llm-args "$USER_LLM_ARGS")
fi

exec "${cmd[@]}"
