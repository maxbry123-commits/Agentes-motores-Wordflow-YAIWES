---
name: rq-audit
description: Formulates research questions and hypotheses from the brief. Checks each RQ for testability (what artifact will answer it?), each hypothesis for falsifiability. Trigger — after the brief in `1-methodology/brief.md` is agreed. Produces `1-methodology/questions-and-hypotheses.md` with an explicit mapping business question → RQ → method. Catches implicit tautologies and overlaps between RQs.
stage: 1.2
status: core
---

# 02-rq-audit

## Why

Between the business question and the interview there's a bridge — research questions and hypotheses. They should be:
- **Testable**: it's clear what the answer will be and how we'll learn it.
- **Falsifiable** (for hypotheses): you can imagine data that would refute it.
- **Non-overlapping** with each other to the point of indistinguishability.
- **Covering** the business question — with no black holes.

## Inputs

- `1-methodology/brief.md` (after `01-brief-intake`).
- (Optional) the researcher's `thoughts.md`.

## Outputs

- `1-methodology/questions-and-hypotheses.md`.
- In chat (assistive) — the list of RQs with testability notes and contentious spots.
- When final — ask the researcher to copy `research_questions` and `hypotheses` into `project-config.yaml`.

### Structure of `questions-and-hypotheses.md`

```markdown
---
type: research_questions
last_updated: TODO
status: draft
---

# Research questions and hypotheses

## RQ1: {{question in one line}}
- **Metric/artifact**: what we'll get in answer (a number, a set of observed paths, quotes of a certain type).
- **Method**: how exactly (in-depth interview / observation / a task for the respondent).
- **Covers guide block**: TODO (after `04-guide-builder`).

## RQ2: ...

## Hypotheses

### H1: {{statement}}
- **Falsifiable by**: what data would refute it.
- **Linked to RQ**: 1, 3.
- **Source**: stakeholder / team / desk research.

### H2: ...

## Mapping

| Business question | RQ | Hypotheses |
|---|---|---|
| ... | RQ1, RQ2 | H1, H3 |
```

## Prompt skeleton

```
You are auditing research questions and hypotheses for a UX study.

Brief:
{{insert `brief.md`}}

Task:
1. Formulate 3–7 research questions that together cover the business question from the brief.
2. Each RQ must be testable — next to it, indicate which research artifact will answer it.
3. Formulate 2–5 hypotheses. Each must be falsifiable — indicate what data would refute it.
4. Make a mapping business question → RQ → methods.
5. Flag:
   - duplicate RQs (one a rephrasing of another);
   - tautological hypotheses ("users use X for Y because they need Y");
   - RQs with no explicit method (often means the task is broader than an in-depth interview).

Don't invent RQs that aren't in the brief. If the brief isn't detailed enough — note what needs clarifying with the stakeholder.
```

The prompt skeleton above is inline — use it as-is, adapting to the brief.

## DoD

- [ ] Each RQ has a stated answer-artifact.
- [ ] Each hypothesis has an explicit falsifier.
- [ ] The mapping covers the business question.
- [ ] In chat (assistive) — a list of contentious spots: "this RQ duplicates that one", "this hypothesis is tautological", "this isn't covered".

## Failure modes

- **Too many RQs** (>7). That's not RQs, that's an interview plan. Cut down to the main ones.
- **RQ without an artifact**: "How do users feel about feature X" — too vague, what artifact answers it? Make it concrete: "What pros and cons do users name for feature X".
- **Hypotheses as rhetorical statements**: "Users want simplicity". That's not a hypothesis, because it can't be refuted. Replace with a testable one: "Users complete task X faster if menu Y is reduced to 5 items".
- **RQs of the "quantitative" category**: "How many users use the feature". That's not in-depth, it's a metric — flag the researcher.

## Mode behavior

- **assistive**: pause after the draft, in chat — contentious spots + a suggestion to "agree and copy into config".
- **autonomous**: write contentious spots into `concerns.md`, choose the most reasonable set of RQs.
