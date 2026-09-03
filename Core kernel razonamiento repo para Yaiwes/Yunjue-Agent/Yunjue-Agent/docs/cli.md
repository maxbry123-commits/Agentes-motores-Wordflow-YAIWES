# CLI Usage (Yunjue Agent)

This document explains how to run the interactive CLI and how to configure it.

## Quick start

After you have completed the repository **Quick Start** setup (virtualenv, dependencies, `.env`, and `conf.yaml`), run:

```bash
python -m cli.cli
```

## Configuration (`conf.yaml`)

The CLI reads model configuration from `conf.yaml`.

- For the meaning of configuration fields, see `docs/configuration_reference.md`.
- In particular, make sure the model blocks used by the CLI are populated (e.g., `BASIC_MODEL`, `VISION_MODEL`, `SUMMARIZE_MODEL`, etc.).

### CLI-specific configuration

`conf.yaml` may also include CLI-related fields:

- `SKILLS_DIR`: Path to the directory that contains your skills (a folder of skill subdirectories, each with a `SKILL.md`).
- `CLI_MODE`: Skill selection mode (`auto` or `manual`).

If `SKILLS_DIR` is set to a path that does not exist, the CLI will create it automatically.

## What the CLI is for

**Yunjue Agent streamlines the path from expertise to action. By simply providing a `SKILL.md`—as we believe high-level experience remains a human-driven asset—the agent autonomously generates the necessary tools to execute those skills. Experience the seamless transformation of documented knowledge into functional automation.**

In other words:

- You write or collect skills as natural-language procedures in `SKILL.md`.
- The agent reads the selected skills and, when needed, generates tools to carry them out.
- You interact with the system through a live streaming interface (messages + tool creation + tool execution).

## Example skills directory

This repository includes an example skills directory at:

- `example/cli/skills`

By default, the CLI uses `example/cli/skills` as the skills directory (unless you override it via `conf.yaml` or via the interactive selector).

