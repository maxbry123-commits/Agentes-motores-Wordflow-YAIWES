# {{RESEARCH NAME}}

> Before you start: open `project-config.yaml` and fill in the project name and mode (`assistive` or `autonomous`). After that, just work.

## What goes where

| Folder | What goes in it |
|---|---|
| `0-input/` | The stakeholder kickoff recording, any materials from them, your own notes before the start. Drop it in — the agent will sort it out. |
| `1-methodology/` | This is where the agent puts drafts: brief, research questions, interview guide, screener. You edit them. |
| `2-interviews/` | Drop interview recordings here. The agent transcribes them, writes a team summary, and codes them. |
| `3-analysis/` | An Obsidian vault. Open it as a vault and you'll see respondent maps, theme maps, findings. The core analysis lives here. |
| `4-output/` | Final artifacts: report, presentation, link to the docs. They appear on your command. |

## Loose files

- `thoughts.md` — your notes and insights about the project. Write whatever you want here — the agent reads it and factors it into the analysis.
- `feedback.md` — what didn't work, what you'd like to fix in the assistant itself. Material for the quarterly retro.
- `project-config.yaml` — mode, model, research questions. Edit as needed.

## How to interact with the agent

Just say what you want:
- "transcribe the last interview"
- "give me a preliminary analysis of what we have so far"
- "let's do the report"
- "format it for the docs"
- "I forgot — what did respondents say about onboarding?"

In `assistive` mode, after every substantive step the agent shows you the result and asks whether to continue. In `autonomous` mode it runs through everything on its own and, at the end, shows you `4-output/handoff.md` with all artifacts and caveats. Read it **before** sharing anything externally.

## Hidden files

`.system/` — the agent's internal files (coded transcripts in JSON, codebook, run logs). You don't need to open these by hand. If you need verbatim quotes or codes, ask the agent and it will produce a readable summary.
