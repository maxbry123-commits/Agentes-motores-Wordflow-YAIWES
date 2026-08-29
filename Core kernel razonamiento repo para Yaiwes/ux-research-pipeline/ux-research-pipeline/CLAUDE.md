# CLAUDE.md

> A thin wrapper for Claude Code. The canon is [`AGENT.md`](AGENT.md). Read it in full **before** any task.

## Start-of-session checklist

**Before answering the researcher anything substantive** in a new chat, read (via the Read tool, in order):

1. [`AGENT.md`](AGENT.md) in full (including §0 hard checklist, §2.7 stop-on-anomaly, §2.8 don't-reinvent).
2. This file (`CLAUDE.md`) in full.
3. [`docs/pipeline-map.md`](docs/pipeline-map.md).
4. [`docs/getting-started.md`](docs/getting-started.md).
5. [`docs/modes.md`](docs/modes.md) (the assistive / autonomous boundary).
6. If the workspace is inside an existing research project (there is a `project-config.yaml` in the root): **first** read `.system/agent-notes.md`, **especially the "Handoff to next session" section** at the very top (if present and `valid: true`, ≤ 7 days old). That section was written by the previous session specifically for you — it tells you which files to read and which **not** to. Follow it; don't duplicate reading. See AGENT.md §14.
7. If the repo root is open: check whether `research-projects/_knowledge/lessons.md` exists — if so, read it.

**Until this checklist is done** — don't create tasks, don't ask the researcher methodological questions, don't propose a plan. This is a silent onboarding: read quietly → answer in one line ("ready, what are we doing?" for a new workspace) or ("continuing `<slug>`, stage `<X>`, blocker `<Y>`. What next?" for an existing project).

## First-run onboarding

**Before substantive work, make sure the environment is ready.** That's your responsibility, not the researcher's.

**The "welcomed" marker.** Before doing anything in onboarding, check whether `.system/welcomed-at.txt` exists in the repo root:

- **No marker** → this is a brand-new user. Run `skills/00-welcome/` (the 3-screen intro, `MISTRAL_API_KEY` via `shared/scripts/setup-mistral.sh`, then write the marker).
- **Marker present** → the user already knows the system. **Don't repeat the welcome.** Quietly run the technical checks below and get to work.

### What to check (quietly, if the marker already exists)

1. **Right workspace.** The client should be opened in the `ux-research-pipeline/` folder (or the plugin installed properly). Signs: `AGENT.md`, `skills/`, `prompts/`, `shared/` are visible alongside.
2. **`.env`.** If missing: tell the researcher that with the default (`coding_mode: agent`) no external LLM keys are needed — only `MISTRAL_API_KEY` if there's audio/video. Offer to create `.env` from `.env.example`. Don't print the YAML in chat.
3. **`RESEARCH_PROJECTS_ROOT`.** Defaults to `<workspace>/research-projects/`. If the folder doesn't exist, `mkdir -p research-projects` without asking (it's infrastructure, not data).
4. **`.gitignore`.** Make sure `research-projects/` and `.env` are ignored. This protects confidential material from an accidental commit.
5. **`skills/ux-transcribe/` present.** It's a vendored skill needed by `06-transcribe`. If missing, that's an installation problem — say so; **don't write your own STT pipeline.** See AGENT.md §2.8.
6. **Python packages.** Before the first run of a Python-using skill (`06-transcribe`, `06.2-speaker-verify`, `shared/scripts/validate-coded.py`):
   ```bash
   python3 -c "import jsonschema, referencing, mistralai, httpx, dotenv" 2>&1
   ```
   On ImportError: `pip install --break-system-packages jsonschema referencing mistralai httpx python-dotenv`.

### When to show onboarding in chat

Only if something actually needs the researcher's input (keys). Everything else — silently. After onboarding: one line, "ready, we can start. What are we doing?" — and don't enumerate what you created unless asked.

---

## Claude-specific notes

1. **TaskCreate / TodoWrite.** Use for any non-trivial task (> 3 steps). Don't show task contents to the researcher in chat — that's your internal kitchen. AGENT.md says "help, don't burden".
2. **AskUserQuestion.** In `assistive` mode this is your main pause-before-a-fork tool. One precise question beats three vague ones. When there are many options, lay out a table in a normal message and ask "agree with the split?" rather than four short choices.
3. **Skills.** Every `skills/*/` folder is a self-contained Claude Code skill. Triggers are in each `SKILL.md`. Invoke them directly; **don't mention their names in chat** with the researcher.
4. **MCP servers.** If the researcher has relevant MCP servers connected (a wiki, an issue tracker, a chat tool), use them to find context. If not, don't push them unless a task genuinely can't be done without one.
5. **Live dashboards.** Use the client's artifact mechanism for **live** research views (the `_index.md` view, the saturation map). Don't use it for final reports or presentations — those go through the formatting/presentation skills as files.

## Intermediate-status rule

Long operations (transcription, coding a batch, a long analysis) — the researcher shouldn't have to wonder whether you're still working.

- When you start a long operation: one short line — "started `<what>`, ETA `<X>` min, monitoring".
- Every 3–5 minutes while it runs: a short update — "Y elapsed, N of M files done".
- On completion: one line with the result.
- **Never go silent for more than ~5 minutes** while something runs in the background.

## Hard ban on a homegrown fallback pipeline

If you hit an unavailable skill or MCP — **don't write your own via direct API calls.** Stop and ask the researcher how to connect the missing tool. One precise question beats an hour of throwaway work. Full rule — AGENT.md §2.8.

Vendored inside the pipeline (no external install needed): `skills/ux-transcribe/` (STT via Voxtral), `skills/transcript-coding/` (API-based coding; run `shared/scripts/install-transcript-coding.sh` once). If a vendored skill is missing on disk, that's an installation problem — say so; don't reinvent it.

## What CLAUDE.md does NOT override from AGENT.md

Everything. `AGENT.md` is the canon. `CLAUDE.md` only adds client-specific hooks.
