# MatTools Evaluation Code

This is the code-only MatTools release used by `evaluation/Tools`. QA
generation, document-generation pipelines, historical outputs, notebooks, large
images, generated RAG corpora, and heavyweight material-science fixture files
have been removed for open-source release hygiene.

## Included

- `src/question_segments/`: public code-only MatTools questions and lightweight
  unit checks.
- `src/claude_cli_test/`: Claude Code read-only runner used by the wrapper.
- `src/result_analysis.py`: optional local evaluator for generated functions.
- `src/tool_source_code/pymatgen/src/pymatgen`: vendored `pymatgen` source code
  used as the read-only source corpus.
- `src/tool_source_code/pymatgen-analysis-defects/tests/*.py`: lightweight
  defects test source files used as code reference only.

The full upstream MatTools fixture corpus is not bundled. Tasks that depended on
large VASP/Q-Chem/defect fixture files were removed from this code-only subset.
Restore the full fixture artifact separately if you need full-data evaluation.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Smoke Test

From `evaluation/Tools`:

```bash
./scripts/run_mattools.sh --parser-self-test
```

This checks parser and trajectory helpers only; it does not call an LLM.

## Run A Small Inference Job

```bash
export MATTOOLS_MODEL=Agents-A1
export CLAUDE_BIN=/path/to/claude  # optional if claude is already on PATH
./scripts/run_mattools.sh
```

Defaults:

- `MATTOOLS_LIMIT=1`
- `MATTOOLS_MAX_PROCESS=1`
- `MATTOOLS_TIMEOUT_SECONDS=600`
- `MATTOOLS_SKIP_EVAL=1`

Code-only subset run:

```bash
MATTOOLS_LIMIT=6 \
MATTOOLS_MAX_PROCESS=2 \
MATTOOLS_SKIP_EVAL=0 \
MATTOOLS_MODEL=Agents-A1 \
./scripts/run_mattools.sh
```

Outputs are written under `src/claude_cli_test/<run-name>/` and must not be
committed.

## Optional Docker Evaluation

The Dockerfile builds a lightweight sandbox for the code-only subset. It installs
`pymatgen` and related packages from package indexes instead of copying removed
large fixture directories.

```bash
docker build -t mat-tool-ben .
```

## Legacy Runners

Legacy single-LLM/RAG runners are kept only as reference code. They read API
credentials from environment variables such as `OPENAI_API_KEY` and
`OPENAI_BASE_URL`; do not commit `.env` files or provider credentials.

## Citation

```bibtex
@misc{MatTools,
      title={MatTools: Benchmarking Large Language Models for Materials Science Tools},
      author={Siyu Liu and Jiamin Xu and Beilin Ye and Bo Hu and David J. Srolovitz and Tongqi Wen},
      year={2025},
      eprint={2505.10852},
      archivePrefix={arXiv},
      primaryClass={cond-mat.mtrl-sci},
      url={https://arxiv.org/abs/2505.10852},
}
```
