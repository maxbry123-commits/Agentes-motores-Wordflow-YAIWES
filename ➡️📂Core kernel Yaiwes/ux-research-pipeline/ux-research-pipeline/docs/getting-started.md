# Getting started

A guide for the researcher. From a zero install to your first study running.

## 1. Installation

### Cowork (recommended for the pilot)

1. Open Cowork.
2. Create a new project, and set the `ux-research-pipeline/` folder as the "selected folder."
3. In the first chat, just say "hi" or describe your task right away.

From there the agent checks the environment itself and asks you what it's missing (usually whether any keys are needed). No manual `cp`, `mkdir`, or hand-editing `.env` — that's its job.

### Production setup (after the first pilots)

Once the pipeline settles, we'll package it as a `.plugin` file and install it as a regular Cowork plugin (Settings → Plugins → Install). After that you can open Cowork in any workspace, and projects will live separately from the plugin code.

### Claude Code / Codex / Cursor / Aider

```bash
git clone <repo-url> ux-research-pipeline
cd ux-research-pipeline
```

Open the folder as a workspace in your client. `CLAUDE.md` (or `AGENTS.md` for Codex/Cursor) is picked up automatically. From there it's the same: write to the agent in chat, and it will ask for keys and create what's needed.

## 2. Your first study

**There's nothing to configure by hand.** Open Cowork in `ux-research-pipeline/` and describe the task in chat:

> "I dropped in a recording of a meeting with the product manager about onboarding for new users. I think it could grow into a full in-depth study."

(You can attach the recording to the message directly, or the agent will ask you to put the file in the right place.)

From there the agent:

1. If this is the first chat in this workspace — quickly checks `.env`, the projects folder, and `.gitignore`. It asks for or creates whatever is needed.
2. Suggests a project name (kebab-case, e.g. `onboarding-2026q2`). One question — confirm or change it.
3. Creates the project folder.
4. Puts the recording in `0-input/`.
5. Transcribes it, analyzes the meeting, and assembles a draft brief in `1-methodology/`.
6. Proposes 2–3 design options (generative / evaluative, sample, method).

## 3. Where projects live

By default — `ux-research-pipeline/research-projects/<slug>/`. In pilot mode this is fine. After the plugin is packaged, they'll move to `~/research-projects/`.

The `research-projects/` folder is automatically added to the plugin's `.gitignore` so that confidential material doesn't end up in the repository.

## 4. After that — it's simple

Drop each interview recording into `2-interviews/`. Within a few minutes:

- Its transcript (`<name>.txt`) and a short team summary appear next to it.
- In `3-analysis/`, the respondent map, themes, and matrix update incrementally.
- Once you've got 5+ interviews — the agent will offer a draft of categories and a paradigm model on its own.

In the chat you get short summaries, no JSON and no skill names. If you want to see what's happening "under the hood" — open `3-analysis/` as an Obsidian vault and you'll see the map of respondents, themes, findings, and the relationship graph.

When there's enough data (the agent will suggest it, usually after 5+ interviews) — you request a findings draft. After that: report, presentation, and wiki write-up on request.

After the report is published, the agent will briefly offer: "here's what we edited along the way, here are the lessons — add them to the shared base?" On a yes, the lessons land in `_knowledge/lessons.md` and will be read when the next projects are created.

## 5. What goes where

Inside a project:

| Folder | Purpose |
|---|---|
| `0-input/` | Meeting recording, notes, materials from the stakeholder. |
| `1-methodology/` | Brief / research questions + hypotheses / interview guide / screener. |
| `2-interviews/` | Audio + transcripts + team summaries. |
| `3-analysis/` | Obsidian vault with maps, the matrix, and the paradigm model. |
| `4-output/` | Final artifacts. |
| `thoughts.md` | Free-form notes (the agent reads this). |
| `feedback.md` | What didn't work (for retrospectives and lessons). |
| `project-config.yaml` | Mode, status, research questions and hypotheses, analysis parameters. |
| `.system/` | Don't touch — this is for the agent. |

Outside, at the `research-projects/` level:

| Folder | Purpose |
|---|---|
| `_knowledge/lessons.md` | Lessons accumulated across projects. Grows after reports are published. |
| `_archive/` | Archived projects (status: archived). |

## 6. Project statuses

In `project-config.yaml` — the `status` field:

- `active` (default) — project in progress.
- `shipped` — report delivered, study closed. Switches automatically after publication.
- `archived` — closed without delivery. By explicit request. The folder moves to `_archive/`.

That's enough. We don't introduce `triage`, `paused`, or `draft`.

## 7. Which keys you need (if the agent asks)

By default (`analysis.coding_mode: agent` in `project-config.yaml`), **no external LLM keys are needed** — the assistant does the coding and analysis itself, in its own context.

What you actually need:

- **`MISTRAL_API_KEY`** — if you'll have audio/video interviews (`06-transcribe` via Voxtral STT). To get it: `https://console.mistral.ai/` → Login → API Keys → Create new. You hand it to the agent in chat, and it saves it to `~/.config/ux-transcribe/.env` via `setup-mistral.sh`. If needed, you can run that same script by hand: `MISTRAL_API_KEY="..." bash shared/scripts/setup-mistral.sh`.
- **`GEMINI_API_KEY`** — only if you'll analyze screenshots via a VLM (`08-screen-vlm`; experimental).

Optional:

- **`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`** — needed only if you switch to `coding_mode: external` (makes sense at ≥10 interviews).

The full list is in `.env.example`, but you don't need to open it by hand — the agent fills it in itself.

## 8. Plan limits and `session_budget`

If you're on a plan with usage limits — that's fine, but **set `session_budget: low` in `project-config.yaml`** (it's the default for new projects, so you can leave it alone).

What this changes:

- **Low budget (`low`):** the agent breaks work into small chunks, pauses more often, and after each heavy skill offers to open a new chat. Less risk of hitting a limit mid-step.
- **Normal (`normal`):** for an unlimited plan or API access. Fewer pauses, only at "weight boundaries" (see AGENT.md §14).
- **High (`high`):** for experienced users without limits. One project — one or two sessions. Use with the understanding that a single error is expensive.

Switching is done by hand in `project-config.yaml`. The agent doesn't change it itself — that's your call.

## 9. A stage boundary = a session boundary

One research project is **many chat sessions**, not one long conversation. At "weight boundaries" (after coding all interviews, after assembling findings, after the stakeholder-facing version of the report) the agent offers to open a new chat:

```
─────────────────────────────────────────
STOP — handoff to a new session
─────────────────────────────────────────
Done: ...
Next step: ...
```

This isn't a glitch or a dodge — a single session's context is finite, and as it bloats, analysis quality degrades. Just:

1. Open a new chat in the same workspace.
2. Copy the first line from the handoff.
3. The agent picks up from the "Handoff to next session" section in `.system/agent-notes.md`.

If the step is short and you don't want to switch — say "let's continue here" and the agent goes on. Silence = wait (the agent won't proceed on its own).

## 10. If something breaks

- **A skill failed midway.** The previous stage's artifact is saved, so you can re-run from that skill alone. In chat, say "re-run coding for R03" or "transcribe it again."
- **The agent hallucinated a quote.** The flat-coding stage (`09-flat-coding`) validates verbatim quotes. If something slipped through — file an issue and mark it in `feedback.md` with the `[hallucination]` category.
- **A skill wasn't found.** All skills are in `skills/` in the repository; names and triggers are in each `SKILL.md`. The stage map is `docs/pipeline-map.md`.
- **You started a new chat and the agent "doesn't remember" where you left off.** That's normal — it restores context from `.system/agent-notes.md` (the "Handoff to next session" section at the top) and other project files. If something specific is lost — remind it in chat, and it'll add it to the notes so it's not lost next time.
- **The agent didn't offer a handoff after a heavy stage.** It should have — that's a hard rule in AGENT.md §14. If it didn't, mark it in `feedback.md` with the `[handoff-skip]` category — that's a bug.

## 11. Don't forget Obsidian (optional, but recommended)

Install [Obsidian](https://obsidian.md) and open your project's `3-analysis/` folder as a vault — you'll see:

- the relationship graph between respondents, themes, and findings,
- maps with frontmatter properties,
- a canvas with the paradigm model.

Everything works without Obsidian (these are just .md files), but you lose the graph view and wikilink navigation.
