# Feedback loop — how the pipeline improves

Every study leaves a trail that later improves the assistant itself. Here's how it works and what you need to do.

## Where the material comes from

From four sources:

1. **`feedback.md`** in each project — the researcher jots down ad hoc what didn't work.
2. **Divergences** between the agent's draft and the final artifact in `4-output/`. In `assistive` mode, every substantive divergence is written to `feedback.md` automatically.
3. **`.system/runs/`** — logs of skill runs: which ran when, on what, and what came out. Objective metrics: time, tokens, retry count.
4. **`.system/prompts-versions/`** — snapshots of the prompts at the time of each run. If a skill changes later, you can compare and do a diagnostic run on the old data.

## Feedback categories

Use (or the agent uses automatically) a fixed taxonomy:

| Category | What it means |
|---|---|
| `hallucination` | the agent invented a fact, quote, number, or name |
| `inaccuracy` | didn't invent it, but interpreted it imprecisely |
| `style` | stylistically poor (tone, structure, length) |
| `insufficient-context` | missed something that was in the material |
| `schema` | output format doesn't match expectations (not Obsidian-friendly, missing timecode, etc.) |
| `ux` | the conversation was awkward — unnecessary questions, missed pauses |
| `security` | something leaked that shouldn't have |
| `other` | everything else |

A strict taxonomy is what lets you aggregate later. Don't invent new categories; instead, add detail in the free-text field.

## What to do with it

### Per-project: lessons extraction after `18-report-draft`

This is an automatic trigger, not a manual one. Once the report draft is assembled, the agent:

1. Walks through `feedback.md` for the project, the diffs between its drafts and the final in `4-output/`, and `.system/agent-notes.md`.
2. Formulates 1–5 short candidate lessons (one rule = one line).
3. In the chat, briefly (3–5 lines): "here are N edits we made along the way; here are the candidate lessons: 1. … 2. … Confirm?".
4. On confirmation — appends them to `RESEARCH_PROJECTS_ROOT/_knowledge/lessons.md` with a date, the project slug, and a category.
5. On rejection — writes nothing; notes in `agent-notes.md` that they were declined.

Record format in `lessons.md`:

```markdown
## YYYY-MM-DD — <project-slug>

- **<category>**: <lesson in one or two lines>. _([project](../<slug>))_
```

Categories: the same as in `feedback.md` (`hallucination`, `inaccuracy`, `style`, `insufficient-context`, `schema`, `ux`, `security`, `other`) plus `methodology`.

When creating the next project (AGENT.md §11.1), the agent reads `lessons.md` in full and uses it as context — but doesn't quote it to the researcher on purpose; that's its own internal kitchen.

### Regular retrospective (quarterly)

1. Gather `feedback.md` from all projects over the quarter, plus the accumulated `_knowledge/lessons.md`.
2. Group by category and by specific skill.
3. Find the top 3 problems by frequency × severity.
4. Decide what to do: edit a prompt in `prompts/` / edit a skill / change a process / add validation.
5. If the fix is a prompt or a skill: make the change, bump the version in the prompt header, archive the old version (in git history or in the `.system/prompts-versions/` of older projects), and run it against the golden set (if one exists).
6. Record it in the skill's or prompt's changelog: "fix X → change Y → expected effect Z".

### Direct in-the-moment edit (when a prompt is clearly broken)

1. Open `prompts/<skill-name>.md` (the skill's production prompt).
2. Find the calibration section (the YAML block in the header) or the relevant place in the body.
3. Make the edit, bump the prompt version (e.g., v0.2 → v0.3), and describe the change in the commit message.
4. If a golden set exists — run it. If not — run the next study on the new version and collect feedback.

## Where the prompts live

Production prompts live in the pipeline's top-level `prompts/` folder, not in the research project. Separate prompt files exist only for the analysis-heavy skills, and they use the short skill name **without** the stage-number prefix — e.g. `prompts/key-findings.md`, not `prompts/17-key-findings.md`. Other skills keep their prompt inline in their own `SKILL.md`. Prompt files are versioned separately from SKILL.md (see `prompts/README.md`). After the pipeline is updated, all researchers start working with the new version.

Snapshots of the prompts that were actually used stay in each project (`.system/prompts-versions/<skill-name>-<timestamp>.md`) — this is what lets you reproduce a run on old data.

## Regression testing (v2)

Once you've accumulated 2–3 closed projects with reference coding, you can set up `tests/golden/`:

```
tests/golden/case-1/
├── input/         ← transcript, brief
├── expected/      ← reference codes, themes, key findings
└── README.md      ← what matters to check in this case
```

`scripts/run-regression.sh` (v2) will walk through every case with the current prompts and compare against the reference. Metrics: coverage, mapping accuracy, false-positive rate in interpretive notes.

While this script doesn't exist yet, drop cases into `tests/golden/` so that enough accumulates for v2.

## What to improve first

Based on the experience of teams already building such pipelines:

1. **Prompts for key findings (`17-key-findings`)** — the most visible artifact, frequently edited, well captured in feedback.
2. **Prompts for the typology (`16-typology`)** — the main risk is substituting demographics for a typology. Errors here are expensive, because the typology goes into the final deliverable.
3. **The quick team summary (`07-quick-summary`)** — its prompt is inline in the skill's own `SKILL.md` (there's no separate file in `prompts/`), so tune it there. Used often, low cost per error, but precisely because it's frequent the cumulative effect is noticeable.

Don't spend time tuning axial-coding prompts in the first quarter — quality there depends heavily on the quality of flat coding, so that's where you should improve first.
