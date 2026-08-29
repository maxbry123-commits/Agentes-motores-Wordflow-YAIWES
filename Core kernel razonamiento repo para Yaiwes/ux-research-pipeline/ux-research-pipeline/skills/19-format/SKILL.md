---
name: format
description: Turns a finished report into a polished, publishable document — clean Markdown (and optional standalone HTML), with mermaid diagrams for the paradigm model / CJM, working anchors, and a table of contents. Trigger — the researcher says "format the report" / "make it presentable" / "export the report". Does NOT edit content — that is the job of 18-report-draft and 18.5-narrative-adapt.
stage: 10.1
status: core
---

# 19-format

## What it does

Takes the narrative-adapted report and produces a clean, well-structured document ready to paste into a wiki, share as a file, or publish. It is a *formatting* step only: it does not rewrite content, restructure sections, or invent metrics.

Two output flavors:

- **`report.md`** — clean GitHub-flavored Markdown with a table of contents, working heading anchors, and mermaid diagrams. The default; works in any Markdown renderer.
- **`report.html`** — optional self-contained HTML (inline CSS, no external assets) for sharing a single file or printing to PDF. Use when the researcher asks for a standalone file.

## Trigger

The researcher explicitly says "format the report" / "make it presentable" / "export" / "I need a shareable version".

In autonomous mode this is **not** called automatically even after `18.5-narrative-adapt` — packaging the final output is a human-gated step. If an input is ready, ask: "ready to format the report?"

## Inputs

- `4-output/report.md` — the version produced by `18.5-narrative-adapt` (adapted language). If it is missing, say: "I need a report first, via `18-report-draft` then `18.5-narrative-adapt`."
- `3-analysis/model.canvas` or the text version of the paradigm model from `18.5` (optional, for the model diagram).
- `3-analysis/typology.md` (optional, for diagrams).
- `project-config.yaml` — `name`, status, research questions for the front matter and title.

## Outputs

- `4-output/report-formatted.md` — the formatted report, ready to paste into a wiki or share.
- `4-output/report.html` — only if the researcher asked for a standalone HTML file.

## Formatting principles (text-first)

- **Text is primary.** Cards, callouts, and diagrams illustrate the text — they never replace it. If a page has more visual blocks than prose, that is a signal to simplify.
- **No technical metrics in the body.** Counts like "N segments", "16 hours of corpus", "72-minute median" are internal process metrics — they do not belong in the stakeholder-facing report. `18.5-narrative-adapt` should already have removed them; do a final check here.
- **Hypothesis-status color semantics** (if you use any callouts/badges): green/blue = confirmed, red = not confirmed, orange = partial. Keep this consistent.
- **Headings and anchors.** Every cross-reference link (`[…](#anchor)`) must resolve to a real heading id. Generate a table of contents from the headings.

## Behavior

1. Check that `4-output/report.md` exists and went through `18.5-narrative-adapt` (front matter should contain `narrative_adapted: true`). If not, tell the researcher which steps are needed.
2. Generate the formatted Markdown:
   - Add/normalize front matter (title from `project-config.yaml`, date, status).
   - Insert a table of contents.
   - Normalize heading levels and ensure anchors resolve.
3. Attach diagrams where they help (optional):
   - **Paradigm model** — from `3-analysis/model.canvas` or the text version in `18.5` → a mermaid `graph LR`. If the model was already rewritten for the stakeholder in `18.5`, use the adapted labels, not the academic "conditions / context / actions / consequences" terms.
   - **CJM / process** — a separate mermaid diagram if the narrative calls for one.
   - Keep diagrams small (≤ 15 nodes). A diagram nobody can read is worse than a list.
4. If the researcher asked for HTML: render the Markdown to a single self-contained `report.html` (inline CSS, no external fonts/scripts, prints cleanly to PDF).
5. Run the QA checklist below. Fix everything before calling it done.

## DoD

- [ ] Table of contents present and every entry links to a real heading.
- [ ] Anchors resolve (each `[…](#…)` has a matching heading id).
- [ ] Mermaid diagrams render (valid syntax, ≤ 15 nodes each).
- [ ] No technical/process metrics leaked into the body ("72-minute median", "2403 segments", etc.).
- [ ] Hypothesis-status colors are correct where used (confirmed = green/blue, not confirmed = red, partial = orange).
- [ ] If HTML was requested: it is self-contained (no external assets) and prints to PDF cleanly.

## Failure modes

- **Mermaid from an Obsidian canvas comes out as a mess.** Obsidian → mermaid is not a clean conversion. It is usually simpler to hand-build a clean mermaid diagram (10–12 nodes telling the story "happens → breaks down → rare success") from the adapted model in `18.5-narrative-adapt`.
- **Report missing `narrative_adapted: true`.** Do NOT run. Say: "the report needs `18.5-narrative-adapt` first, otherwise a raw draft with jargon and percentages will ship."
- **Broken anchors after auto-generating the TOC.** Slugify heading text consistently and verify each link before finishing.

## What it does NOT do

- **Does not edit report content.** Language and style edits are `18.5-narrative-adapt`. Structural edits are `18-report-draft`.
- **Does not make structural changes** (new sections, reordering).
- **Does not publish anywhere** without explicit confirmation in chat. If the team uses a wiki or BI tool, the researcher copies the output there; this skill only produces the file.

## After this pass

After `19-format` the output side of the pipeline is considered complete. The lessons-extraction trigger already fired in `18-report-draft`; nothing extra needs to be written to `_knowledge/lessons.md` here.

If, while formatting, you notice something new (e.g. a layout that systematically does not fit a certain report type), add a lessons candidate and ask the researcher.
