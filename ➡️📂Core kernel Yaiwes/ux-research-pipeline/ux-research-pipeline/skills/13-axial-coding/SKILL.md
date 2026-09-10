---
name: axial-coding
description: Groups flat codes into categories and axes, building the first draft of the category system. Trigger — 5+ coded interviews. The main analysis skill. In assistive mode it proposes categories, the researcher edits, and the skill re-glues them. The main risk is premature closure of categories and the loss of rare but important codes. Works across ALL interviews at once, not per-respondent.
stage: 8.3
status: stretch
---

# 13-axial-coding

## Why

Flat codes (`09-flat-coding`) stay close to the respondents' words, with no hierarchy. To get a structure for analysis and the report, they need to be grouped into categories and connected along axes.

This is the **main analysis skill**. The quality of the whole report depends on how well the grouping is done here.

## Trigger

After 5+ coded interviews.

Can be re-run after each new interview — categories expand and get re-glued.

## Inputs

- All `.system/coded/*.json` (flat codes by segment).
- `.system/links.json` (from `12-link-detector`) — substantive links.
- `3-analysis/themes/*.md` (the current theme system).

## Outputs

- `3-analysis/themes/<slug>.md` — a Markdown map per theme, valid against `theme.v1` (frontmatter + body). Template in `prompts/axial-coding.md`.
- `3-analysis/_categories.md` — a consolidated document with the system of categories and axes.
- `.system/axial/<timestamp>/themes.json` — a JSON snapshot of all themes per the `shared/schemas/theme.v1.schema.json` schema.
- `.system/axial/<timestamp>/categories.json` — a JSON snapshot of categories per `shared/schemas/category.v1.schema.json`.

Downstream skills (`14-paradigmatic-model`, `17-key-findings`) read the JSON snapshots; the Markdown maps are for the researcher in Obsidian.

## Production prompt

The full prompt with the `_categories.md` and `themes/<slug>.md` templates, anti-pattern checks, and the algorithm lives in `prompts/axial-coding.md`. This SKILL.md describes the skill contract; the prompt is versioned separately.

## DoD

- [ ] 4–8 categories, no more.
- [ ] 1–3 axes.
- [ ] Each category pinned to at least 3 respondents.
- [ ] The "didn't fit" section is filled in (don't skip it).
- [ ] Themes in `3-analysis/themes/` are updated — frontmatter contains `category` and `axis`.

## Failure modes

- **A too-beautiful hierarchy = no data that breaks it.** This is always a bad sign. If you have a neat 4 categories of 5 themes each, double-check that you haven't discarded something.
- **Textbook categories** ("motivations", "pain points", "expectations"). That's a platitude, not the categories of a specific study. Categories should sound about **this** product and **these** respondents.
- **Premature closure.** After 5 interviews the system may seem ready, but the 6th interview will break it. Don't finalize early; mark categories `status: emerging` while interviews continue.
- **Demographic axes.** "On the age axis, young vs. older" is not axial coding, it's statistics. Axes are about differences in behavior, motivation, attitude.
- **All codes in one category.** Over-generalization. Split it up.

## Mode behavior

- **assistive**: after the pass, a pause and 1–2 sentences in chat: "here's what's taking shape, take a look at `_categories.md`. Especially the 'didn't fit' section." Wait for the researcher's reaction.
- **autonomous**: write the system, and in `concerns.md` record the top-3 uncertainties about categories ("category X is pinned to only 3 respondents from one segment; it may turn out to be a segment effect").
