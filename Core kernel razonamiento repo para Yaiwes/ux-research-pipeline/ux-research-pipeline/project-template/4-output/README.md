# 4-output

The final artifacts you share externally.

## What appears here

Only on your request. The agent never puts anything here on its own without an explicit "let's do the report / presentation / publish it to the docs."

- `report.md` — the text report. Structure: executive → findings → evidence → recommendations → appendices.
- `report-formatted.md` — the docs version (Markdown formatting, a separate file so it doesn't get confused with the local one).
- `presentation.pptx` — the presentation. Generated from `report.md` + the key findings.
- `handoff.md` — **autonomous mode only.** A summary: what the agent did, the key findings, **`concerns.md`**: where it's unsure, where data is thin. **Read it before sharing externally.**
- `concerns.md` — **autonomous mode only.** All methodological compromises and "not sure" spots.

## What to do next

After the agent has assembled the report:
1. Read it. Fix what's wrong.
2. Tell the agent "format it for the docs" — it will run the Markdown formatting step (the docs publishing requires the relevant token in `.env`).
3. Tell the agent "make a presentation" — it will assemble the `.pptx` via the presentation export step.

If a new thought or interpretation showed up in your edit, it's better to tell the agent about it in words so it factors it into the other artifacts (for example, the presentation). Otherwise your edits to one file stay isolated.
