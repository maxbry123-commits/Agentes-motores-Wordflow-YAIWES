# MolBench / MolClaw Evaluation Code

This directory contains the code-first MolBench/MolClaw evaluation harness used
by Agents-A1. Data-construction utilities, training-export utilities, historical
baseline logs, notebooks, large images, and oracle pickle artifacts are removed.

## Included

- `molbench/data/molbench-ms-*`: original lightweight MolBench molecular-screening data.
- `molbench/data/molbench-mo`: original lightweight molecular-optimization data.
- `molbench/eval`: deterministic evaluator code for prediction folders.
- `molclaw_run/infer/baselines`: OpenAI-compatible direct baseline runner.
- `molclaw_run/infer/claude_agent`: Claude Code agent runner.
- `skills`: benchmark-facing chemistry skills used by the Claude Code runner.
- `config`: configs for MolBench and ChemCoTBench-compatible runs.

ChemCoTBench oracle pickle files are external artifacts. To run oracle-based
ChemCoTBench evaluation, restore the official files to:

```text
molbench/eval/ChemCoTBench/baseline_and_eval/oracle/
```

Expected files include `drd2_current.pkl`, `gsk3b_current.pkl`, `jnk3_current.pkl`,
and `fpscores.pkl`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

If editable install is insufficient for a task, use the upstream Conda
environment from `environment.yaml`.

## Run Direct Baseline

```bash
export OPENAI_API_KEY=<YOUR_API_KEY>
export OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1
bash molclaw_run/infer/baselines/launch_baseline.sh \
  --cfg config/baseline_molbench-ms-1.yaml
```

The launcher prints `RESULTS_DIR=...` and then runs evaluation.

## Evaluate Existing Results

```bash
python molbench/eval/run_eval_bench.py <RESULTS_DIR> \
  --cfg config/baseline_molbench-ms-1.yaml
```

Evaluation writes `<RESULTS_DIR>/bench_scores.json`.

## Notes

- Do not commit `.env`, local result folders, provider logs, request logs, or restored oracle artifacts.
- Generated outputs are ignored by the parent `evaluation/Tools/.gitignore`.
- ChemCoTBench oracle-based eval fails fast with a setup error when oracle artifacts are absent.
