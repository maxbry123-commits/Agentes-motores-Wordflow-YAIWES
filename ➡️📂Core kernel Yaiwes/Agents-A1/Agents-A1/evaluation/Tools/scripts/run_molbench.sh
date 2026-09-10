#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BENCH_DIR="$TOOLS_DIR/molbench"
PYTHON_BIN="${PYTHON_BIN:-python}"

export PYTHONPATH="$BENCH_DIR/..:$BENCH_DIR${PYTHONPATH:+:$PYTHONPATH}"
if [[ "$PYTHON_BIN" == */* ]]; then
  export PATH="$(cd "$(dirname "$PYTHON_BIN")" && pwd):$PATH"
fi
cd "$BENCH_DIR"

case "${1:-}" in
  smoke|test|--smoke)
    exec "$PYTHON_BIN" - <<'PY'
from pathlib import Path
import py_compile
root = Path.cwd()
for rel in [
    "MolClaw/__init__.py",
    "molbench/eval/run_eval_bench.py",
    "molbench/eval/eval_runner.py",
    "molclaw_run/data_loader/bench_loaders.py",
    "molclaw_run/infer/baselines/run_baseline.py",
    "molclaw_run/infer/claude_agent/run_claude.py",
]:
    py_compile.compile(str(root / rel), doraise=True)
print("molbench smoke ok")
PY
    ;;
  eval)
    shift
    exec "$PYTHON_BIN" molbench/eval/run_eval_bench.py "$@"
    ;;
  baseline)
    shift
    exec bash molclaw_run/infer/baselines/launch_baseline.sh "$@"
    ;;
  claude)
    shift
    exec bash molclaw_run/infer/claude_agent/launch_claude.sh "$@"
    ;;
  -h|--help)
    cat <<'HELP'
Usage:
  scripts/run_molbench.sh smoke
  scripts/run_molbench.sh baseline --cfg config/baseline_molbench-ms-1.yaml
  scripts/run_molbench.sh eval <RESULTS_DIR> --cfg <CONFIG_PATH>
  MODEL=<model> OPENAI_API_KEY=... scripts/run_molbench.sh

No-argument mode runs the direct baseline with MOLBENCH_CONFIG, defaulting to
config/baseline_molbench-ms-1.yaml. Set MOLBENCH_FULL=1 for the five original
MolBench configs.
HELP
    exit 0
    ;;
esac

export MODEL_NAME="${MOLBENCH_MODEL:-${MODEL:-${MODEL_NAME:-Agents-A1}}}"

if [[ "${MOLBENCH_FULL:-0}" == "1" ]]; then
  configs=(
    config/baseline_molbench-ms-1.yaml
    config/baseline_molbench-ms-2.yaml
    config/baseline_molbench-ms-3.yaml
    config/chemcot_mo_edit.yaml
    config/chemcot_mo_opt.yaml
  )
  for cfg in "${configs[@]}"; do
    bash molclaw_run/infer/baselines/launch_baseline.sh --cfg "$cfg"
  done
else
  cfg="${MOLBENCH_CONFIG:-config/baseline_molbench-ms-1.yaml}"
  exec bash molclaw_run/infer/baselines/launch_baseline.sh --cfg "$cfg"
fi
