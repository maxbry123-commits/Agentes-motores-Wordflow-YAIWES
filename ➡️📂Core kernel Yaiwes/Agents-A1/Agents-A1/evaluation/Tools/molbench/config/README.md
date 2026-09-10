# MolBench Configs

This directory keeps minimal runnable configs for the original MolBench/MolClaw
evaluation tasks only.

## Included Configs

- `baseline_molbench-ms-1.yaml`: direct LLM baseline on `rdkit_bench`.
- `baseline_molbench-ms-2.yaml`: direct LLM baseline on `acnet_curated`.
- `baseline_molbench-ms-3.yaml`: direct LLM baseline on `molbench_vs`.
- `chemcot_mo_edit.yaml`: direct LLM baseline on original MolBench molecule editing data.
- `chemcot_mo_opt.yaml`: direct LLM baseline on original MolBench molecule optimization data.
- `claude_template.yaml`: template for Claude Code agent evaluation.

## Credentials

Do not put API keys in YAML configs. Use environment variables:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_BASE_URL`

Keep local `.env` files untracked.
