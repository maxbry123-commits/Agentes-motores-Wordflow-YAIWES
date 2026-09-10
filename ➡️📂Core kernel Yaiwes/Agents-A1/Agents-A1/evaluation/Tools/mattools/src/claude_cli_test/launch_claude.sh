#!/bin/bash
# Claude Code method1 read-only inference -> original MatTools evaluation.

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
cd "$SRC_DIR" || exit 1

CLAUDE_BIN="${CLAUDE_BIN:-$REPO_ROOT/scripts/claude-code.sh}"
MODEL="${CLAUDE_MODEL:-${ANTHROPIC_MODEL:-sonnet}}"
RUN_NAME=""
LIMIT=""
TIMEOUT=""
MAX_PROCESS="1"
CLAUDE_EXTRA_ARGS=()
PYTHON_CMD=()
SKIP_EVAL="0"
RESUME_EXISTING="0"
REBUILD_ONLY="0"

usage() {
  echo "Usage: bash claude_cli_test/launch_claude.sh [--claude-bin PATH] [--model MODEL] [--run-name NAME] [--limit N] [--timeout SEC] [--max-process N] [--resume-existing] [--rebuild-only] [--skip-eval] [--claude-extra-args ...]"
  echo "Default --claude-bin: $REPO_ROOT/scripts/claude-code.sh"
  echo "Default condition: method1_read_only with Read,Grep,Glob over tool_source_code/pymatgen/src/pymatgen"
  echo "Use --skip-eval for rlaunch/remote inference; result_analysis.py requires local Docker access."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude-bin)
      CLAUDE_BIN="${2:-}"
      if [[ -z "$CLAUDE_BIN" ]]; then
        echo "Error: --claude-bin requires a value."
        exit 1
      fi
      shift 2
      ;;
    --model)
      MODEL="${2:-}"
      if [[ -z "$MODEL" ]]; then
        echo "Error: --model requires a value."
        exit 1
      fi
      shift 2
      ;;
    --run-name)
      RUN_NAME="${2:-}"
      if [[ -z "$RUN_NAME" ]]; then
        echo "Error: --run-name requires a value."
        exit 1
      fi
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      if [[ -z "$LIMIT" ]]; then
        echo "Error: --limit requires a value."
        exit 1
      fi
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:-}"
      if [[ -z "$TIMEOUT" ]]; then
        echo "Error: --timeout requires a value."
        exit 1
      fi
      shift 2
      ;;
    --max-process)
      MAX_PROCESS="${2:-}"
      if [[ -z "$MAX_PROCESS" ]]; then
        echo "Error: --max-process requires a value."
        exit 1
      fi
      shift 2
      ;;
    --skip-eval|--inference-only)
      SKIP_EVAL="1"
      shift
      ;;
    --resume-existing)
      RESUME_EXISTING="1"
      shift
      ;;
    --rebuild-only)
      REBUILD_ONLY="1"
      shift
      ;;
    --claude-extra-args)
      shift
      CLAUDE_EXTRA_ARGS=("$@")
      break
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

cmd=(
  "$SCRIPT_DIR/build_agent.py"
  --claude-bin "$CLAUDE_BIN"
  --model "$MODEL"
  --max-process "$MAX_PROCESS"
)
if [[ -n "$RUN_NAME" ]]; then
  cmd+=(--run-name "$RUN_NAME")
fi
if [[ -n "$LIMIT" ]]; then
  cmd+=(--limit "$LIMIT")
fi
if [[ -n "$TIMEOUT" ]]; then
  cmd+=(--timeout "$TIMEOUT")
fi
if [[ "$RESUME_EXISTING" == "1" ]]; then
  cmd+=(--resume-existing)
fi
if [[ "$REBUILD_ONLY" == "1" ]]; then
  cmd+=(--rebuild-only)
fi
if [[ ${#CLAUDE_EXTRA_ARGS[@]} -gt 0 ]]; then
  cmd+=(--claude-extra-args "${CLAUDE_EXTRA_ARGS[@]}")
fi

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON_CMD=("$PYTHON_BIN")
elif command -v uv >/dev/null 2>&1 && [[ -f "$REPO_ROOT/pyproject.toml" ]] && [[ "${VIRTUAL_ENV:-}" != "$REPO_ROOT/.venv" ]]; then
  PYTHON_CMD=(uv run --frozen --project "$REPO_ROOT" python)
else
  PYTHON_CMD=(python)
fi

tmp_log="$(mktemp -t mattools_claude_out.XXXXXX)"
PYTHONUNBUFFERED=1 "${PYTHON_CMD[@]}" "${cmd[@]}" 2>&1 | tee "$tmp_log"
py_status=${PIPESTATUS[0]}
if [[ "$py_status" -ne 0 ]]; then
  exit "$py_status"
fi

results_dir="$(grep '^RESULTS_DIR=' "$tmp_log" | tail -1 | sed 's/^RESULTS_DIR=//')"
rm -f "$tmp_log"
if [[ -z "$results_dir" ]]; then
  echo "Error: build_agent.py did not emit RESULTS_DIR=..."
  exit 1
fi

if [[ "$SKIP_EVAL" == "1" ]]; then
  echo "[Claude MatTools] Skipping Docker evaluation. Run result_analysis.py locally on RESULTS_DIR."
  exit 0
fi

eval_cmd=("$SRC_DIR/result_analysis.py" --generated_function_path "$results_dir")
if [[ "$LIMIT" =~ ^[0-9]+$ ]] && (( LIMIT > 0 )); then
  eval_cmd+=(--limit "$LIMIT" --allow-partial)
fi

"${PYTHON_CMD[@]}" "${eval_cmd[@]}"
