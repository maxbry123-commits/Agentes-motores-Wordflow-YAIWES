# Tools Evaluation Benchmarks

This directory contains the code-first, open-source release of the tool-use
benchmarks used for Agents-A1 evaluation. It keeps benchmark runners, wrappers,
lightweight task/config files, and safe documentation. Large binary fixtures,
model oracle pickles, generated document corpora, historical logs, and private
local artifacts are intentionally not included.

## Directory Layout

| Path | Benchmark | Notes |
| --- | --- | --- |
| `tau2/` | tau2-bench | Original tau2 evaluation code and original task JSON. Synthetic-task and SFT-generation files are removed. |
| `mattools/` | MatTools | Code-only MatTools subset with source corpus and lightweight questions. Heavy material-science fixture files are removed. |
| `molbench/` | MolBench / MolClaw | MolBench/MolClaw runners, configs, lightweight data, and evaluators. ChemCoTBench oracle pickles are external artifacts. |
| `vita/` | VitaBench | VitaBench source, configs, and task JSON. Generated results and image assets are removed. |
| `scripts/` | Wrapper scripts | Thin launchers that resolve paths relative to this directory and call each benchmark's native entrypoint. |

## Code-Only Release Notes

This tree is suitable for source release and wrapper-level smoke tests. It does
not bundle large artifacts that are better distributed separately:

- MatTools: vendored `pymatgen` test fixture data, generated RAG/document JSON,
  notebooks, and large images are removed. The public subset keeps only tasks
  that do not require those fixture files.
- MolBench: ChemCoTBench oracle pickle files under
  `molbench/molbench/eval/ChemCoTBench/baseline_and_eval/oracle/` are not
  included. Restore them from the official/internal artifact before running
  ChemCoTBench oracle-based full evaluation.
- tau2/VitaBench: original task JSON is retained, but generated simulations,
  caches, build directories, and README image assets are removed.

Do not commit API keys, `.env` files, local provider configs, generated result
folders, notebooks, model outputs, or restored heavyweight artifacts.

## Common Setup

Use one environment per benchmark when possible, because dependency sets differ.
The wrappers do not install dependencies; they only launch the benchmark.

```bash
cd evaluation/Tools
```

Common environment variables:

| Variable | Used by | Meaning |
| --- | --- | --- |
| `MODEL` | all wrappers | Default model name. Defaults to `Agents-A1` in wrappers. |
| `USER_MODEL` | `tau2`, `vita` | User simulator model. Defaults to `deepseek-v3.2`. |
| `EVALUATOR_MODEL` | `vita` | Evaluator/judger model. Defaults to `deepseek-v3.2`. |
| `OPENAI_API_KEY` | OpenAI-compatible runners | API key exported in the shell only. |
| `OPENAI_BASE_URL` | OpenAI-compatible runners | Optional OpenAI-compatible base URL. |
| `ANTHROPIC_AUTH_TOKEN` | Claude Code runners | Token for Anthropic-compatible Claude Code endpoints. |
| `ANTHROPIC_BASE_URL` | Claude Code runners | Optional Anthropic-compatible base URL. |
| `PYTHON_BIN` | all wrappers | Python executable. Defaults to `python`. |

## tau2

Install:

```bash
cd tau2
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

If the default mirror is unreliable:

```bash
PIP_CONFIG_FILE=/dev/null pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Smoke test:

```bash
../scripts/run_tau2.sh check-data
```

Small model evaluation:

```bash
export MODEL=Agents-A1
export USER_MODEL=deepseek-v3.2
../scripts/run_tau2.sh
```

Useful overrides:

```bash
TAU2_DOMAIN=retail \
TAU2_NUM_TASKS=10 \
TAU2_NUM_TRIALS=1 \
TAU2_MAX_CONCURRENCY=2 \
TAU2_AGENT_LLM="$MODEL" \
TAU2_USER_LLM="$USER_MODEL" \
../scripts/run_tau2.sh
```

For OpenAI-compatible endpoints, pass LiteLLM args as JSON:

```bash
export TAU2_AGENT_LLM_ARGS='{"temperature":0,"api_key":"<YOUR_API_KEY>","api_base":"<YOUR_BASE_URL>"}'
export TAU2_USER_LLM_ARGS="$TAU2_AGENT_LLM_ARGS"
../scripts/run_tau2.sh
```

Outputs are written under `tau2/data/simulations/` and are ignored.

## MatTools

MatTools is released here as a code-only subset. The runner can still generate
functions against the local `pymatgen` source corpus, but tasks requiring removed
VASP/Q-Chem/defect fixture files are not included in the public subset.

Install:

```bash
cd mattools
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Smoke test:

```bash
../scripts/run_mattools.sh --parser-self-test
```

Small Claude Code run:

```bash
export MATTOOLS_MODEL=Agents-A1
# Optional if claude is already on PATH.
export CLAUDE_BIN=/path/to/claude
../scripts/run_mattools.sh
```

Useful overrides:

```bash
MATTOOLS_LIMIT=6 \
MATTOOLS_MAX_PROCESS=2 \
MATTOOLS_SKIP_EVAL=0 \
MATTOOLS_MODEL=Agents-A1 \
../scripts/run_mattools.sh
```

Inference outputs are written under `mattools/src/claude_cli_test/<run-name>/`
and are ignored.

## MolBench / MolClaw

Install:

```bash
cd molbench
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the lightweight MS-1 direct baseline:

```bash
pip install openai PyYAML tqdm pandas rdkit scikit-learn requests networkx numpy
pip install --no-deps -e .
```

Smoke test:

```bash
../scripts/run_molbench.sh smoke
```

Small direct-baseline evaluation:

```bash
export MODEL=Agents-A1
export OPENAI_API_KEY=<YOUR_API_KEY>
export OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1
../scripts/run_molbench.sh
```

Run another config:

```bash
MOLBENCH_CONFIG=config/baseline_molbench-ms-2.yaml ../scripts/run_molbench.sh
```

ChemCoTBench oracle-based evaluation requires external oracle pickle artifacts
restored to `molbench/molbench/eval/ChemCoTBench/baseline_and_eval/oracle/`.
Without those files, the evaluator fails with an explicit setup error.

Outputs are written under `molbench/results/agent_prediction/<run-name>/` and
are ignored.

## VitaBench

VitaBench loads model settings from `src/vita/models.yaml` or the path set by
`VITA_MODEL_CONFIG_PATH`. The committed `models_example.yaml` is a safe template;
create a local config before model calls.

Install:

```bash
cd vita
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp src/vita/models_example.yaml src/vita/models.yaml
# Edit src/vita/models.yaml with your provider URL and API key.
```

If the default mirror is unreliable:

```bash
PIP_CONFIG_FILE=/dev/null pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Smoke test:

```bash
../scripts/run_vita.sh --help
```

Small model evaluation:

```bash
export VITA_MODEL_CONFIG_PATH="$PWD/src/vita/models.yaml"
export MODEL=Agents-A1
export USER_MODEL=deepseek-v3.2
export EVALUATOR_MODEL=deepseek-v3.2
../scripts/run_vita.sh
```

Useful overrides:

```bash
VITA_DOMAIN=delivery,instore,ota \
VITA_LANGUAGE=english \
VITA_NUM_TASKS=5 \
VITA_MAX_CONCURRENCY=2 \
VITA_MODEL="$MODEL" \
VITA_USER_MODEL="$USER_MODEL" \
VITA_EVALUATOR_MODEL="$EVALUATOR_MODEL" \
../scripts/run_vita.sh
```

Outputs are written under `vita/data/simulations/` and are ignored.
