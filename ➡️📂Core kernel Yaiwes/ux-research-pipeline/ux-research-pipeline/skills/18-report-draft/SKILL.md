---
name: report-draft
description: Assembles the report draft (text + recommendations). Trigger — the researcher says "let's do the report" / in autonomous after `17-key-findings`. Structure — executive summary → findings → evidence → recommendations → appendices. All quotes are verbatim with timecodes. Recommendations are explicitly marked `[draft]` and linked to findings. Merges 9.1 (draft) + 9.2 (recommendations).
stage: 9.1+9.2
status: core
---

# 18-report-draft

## Why

The final research document — what the stakeholder and the team will see. The main risks:
- **Boilerplate** ("the study revealed that…") with no substance.
- **Hallucinated quotes** — the most serious error; requires verbatim validation.
- **Recommendations divorced from findings** — recommendations with no clear link to a specific finding.

## Trigger

- The researcher explicitly said "let's do the report" / "I need a report draft."
- In autonomous: automatically after `17-key-findings`.

## Inputs

- `3-analysis/findings.md` + `3-analysis/findings/F0X.md`.
- `3-analysis/typology.md` (if any).
- `3-analysis/model.md` (for an optional section).
- `1-methodology/brief.md`.
- `1-methodology/questions-and-hypotheses.md`.
- `1-methodology/desk-research.md` (if any).
- All `.system/coded/*.json` (for verbatim checks).
- `thoughts.md` — the researcher's notes.

## Outputs

- `4-output/outline.md` — the **intermediate** plan of report sections (Step 1, see below). Kept until `18.5-narrative-adapt` finishes, then moved to `.system/archive/`.
- `4-output/report.md` — the main report (Step 3).

## Two-beat process: outline → confirmation → text

The skill consists of **three steps**. Steps 1 → 2 → 3 are strictly sequential; Step 3 does not start without explicit confirmation from the researcher at Step 2.

### Step 1: outline

Generate `4-output/outline.md` — the plan of sections for the future report.

Contents of `outline.md`:

```markdown
---
type: report-outline
project: <slug>
date: YYYY-MM-DD
status: draft
findings_count: <N>
respondents_count: <N>
estimated_pages: <X-Y>
---

# Report outline — <project name>

## Structure (heading tree, levels 2–3)

### 1. Executive summary
**What's inside:** 2–3 paragraphs — the main conclusion in 30 seconds.
**Length:** ~300 words.

### 2. About the project
**What's inside:** business question, method, period, sample (N + segments).
**Length:** ~150 words.

### 3. Research questions and short answers
**What's inside:** a table of RQ → a 1–2 sentence answer.
**Length:** a 4–6 row table.

### 4. Key findings
**What's inside:** F1..FN, each one — statement + an expanded paragraph + 2–3 verbatim quotes + boundaries of applicability + confidence.
**Length:** ~200–300 words per finding, ~5–7 findings total.

### 5. Typology
**What's inside:** <if built — a description of the types; if not — skip the section>.
**Length:** ~400 words or 0.

### 6. Paradigm model
**What's inside:** <a reference to the model + 2–3 paragraphs on the dynamics; if the researcher doesn't want it in the main report — move the section to an appendix>.
**Length:** ~300 words or moved to an appendix.

### 7. What we did not find
**What's inside:** hypotheses that did not hold up — that is also a result.
**Length:** ~200 words.

### 8. Recommendations `[draft]`
**What's inside:** R1..RM marked [draft], linked to specific findings.
**Length:** ~150 words per recommendation, ~3–5 total.

### 9. New hypotheses
**What's inside:** patterns that were not in the original brief — material for the next RQ.
**Length:** ~200 words.

### 10. Methodological caveats
**What's inside:** limitations of the sample and the method.
**Length:** ~150 words.

### 11. Appendices
**What's inside:** a list of links to transcripts, cards, the matrix.
```

In the outline:
- **Do not write the actual finding text** — only their one-line statements.
- **Do not invent sections** that aren't in the standard structure. If the researcher previously said "I want a section on X" — note it here.
- **If some data is missing** (e.g. there is no typology) — mark the section as "skip" with a rationale.
- Length estimates in words or paragraphs, not pages (pages depend on layout).

### Step 2: agreeing with the researcher (explicit STOP)

After writing `outline.md` — **stop immediately** and ask the researcher. Message template:

```
I've written the report plan to `4-output/outline.md`. Before I write the full text,
please take a look and tell me:

- is the order of sections OK?
- anything to remove (e.g. move the paradigm model to an appendix / skip the typology)?
- anything to add (your own section, emphasis on a specific finding)?
- are the lengths realistic?

Once you confirm, I'll write the full text. I'll take edits in any form:
changes directly in `outline.md` or a comment in chat.
```

**Do not start Step 3 without an explicit "OK, go" / "looks good" / "continue" from the researcher.** Silence ≠ confirmation.

If the researcher sends edits — apply them to `outline.md`, **ask again** (a brief summary of the changes + "OK now?"), and only after confirmation move to Step 3.

### Step 3: full text

Only after the outline is confirmed — write the full `4-output/report.md` per the agreed plan. The frontmatter must contain:

```yaml
---
type: report
project: <slug>
date: YYYY-MM-DD
status: draft
findings_count: <N>
respondents_count: <N>
outline_approved: true        # critical gate — without it 18.5 will not run
outline_approved_at: YYYY-MM-DD HH:MM
---
```

If `outline_approved: true` is missing — `18.5-narrative-adapt` must refuse to work and ask you to go back to Step 2.

## Report structure

```markdown
---
type: report
project: TODO
date: TODO
status: draft
findings_count: 0
respondents_count: 0
---

# Report — {{project name}}

## Executive summary
{{2–3 paragraphs: the essentials in 30 seconds of reading. Business question → key findings → main recommendations.}}

## About the project

**Business question**: {{from the brief}}.
**Method**: {{N in-depth interviews with {{segments}}}}.
**Period**: {{dates}}.

## Research questions and short answers

| RQ | Answer |
|---|---|
| RQ1: ... | {{1–2 sentences}} |
| RQ2: ... | ... |

## Key findings

### F1: {{statement}}

{{an expanded paragraph with grounding}}

**Evidence:**
- > "{{verbatim}}" — {{R0X, segment}} `[mm:ss]`
- > "{{verbatim}}" — {{R0Y, segment}} `[mm:ss]`
- {{N respondents in the sample mentioned it}}.

**Boundaries of applicability:** {{where it does not hold}}.

**Confidence:** medium/high.

### F2: ...

## Typology (if any)

{{description of the types, see `3-analysis/typology.md`}}

## Paradigm model (optional)

{{description of the dynamics, see `3-analysis/model.md` or insert the canvas image}}

## What we did not find (though we looked)

(hypotheses that did NOT hold up — that is also a result)

## Recommendations `[draft]`

> **Note**: the recommendations are a draft. The final version requires a joint discussion with the product manager and the designer.

### R1 — based on F1
- **What we do**: {{a specific action}}.
- **Who it's addressed to**: {{the onboarding / search / etc. team}}.
- **Why**: a reference to F1.
- **Expected effect**: {{what will change}}.
- **Priority**: high/medium/low.
- **Depends on**: {{what needs to happen first}}.

### R2 — ...

## New hypotheses for the next study

(patterns that were NOT in the original brief — material for the next RQ)

## Methodological caveats

- {{sample limitations}}.
- {{method limitations}}.
- {{what needs additional checking — e.g. quantitatively}}.

## Appendices

- Full transcripts: `2-interviews/` (internal access).
- Respondent cards: `3-analysis/respondents/`.
- Codes and categories: `3-analysis/_categories.md`.
- Saturation map: `3-analysis/matrix.xlsx`.
```

## Production prompt

The full prompt — with the `report.md` template, verbatim-check rules, the list of banned boilerplate phrases, and the per-section algorithm — is in `prompts/report-draft.md`. This SKILL.md describes the skill's contract; the prompt is versioned separately.

A JSON schema for the report is not introduced for now — the report stays a Markdown document (read by the stakeholder), and the machine-validatable data already lives in the upstream schemas (`finding.v1`, `typology-type.v1`, etc.).

## DoD

- [ ] `4-output/outline.md` created at Step 1.
- [ ] The researcher confirmed the outline in chat; the confirmation is recorded in `agent-notes.md`.
- [ ] `outline_approved: true` and `outline_approved_at: <date>` written into the frontmatter of `4-output/report.md`.
- [ ] All quotes passed the verbatim check.
- [ ] The executive summary does not exceed 3 paragraphs.
- [ ] Every finding is linked to an RQ.
- [ ] Every recommendation is linked to a finding.
- [ ] The "what we did not find" section is filled in.
- [ ] The "methodological caveats" section is filled in.
- [ ] Recommendations are marked `[draft]`.

## Failure modes

- **A quote could not be found word-for-word** — do NOT put it in quotation marks; paraphrase it without quotes or delete it.
- **A generic recommendation** ("improve the UX"). Be specific: "move button X on page Y, because R03 and R07 couldn't find it in its current position."
- **The executive summary does not answer the business question.** Rewrite it. If you can't — flag: "the business question is not sufficiently covered by the data."
- **The report is too long (>20 pages).** Split it into main + appendix; keep only the executive + findings + key recommendations in the main part.
- **The report = a retelling of the interviews.** This is the most common error. If, while reading, you only learn "what they said" (and not "what it means" and "what to do") — redo it.

## Mode behavior

- **assistive**:
  - **Step 1** — write `outline.md`, in chat briefly: "the report plan is in `4-output/outline.md`. Take a look: order, what to remove/add, are the lengths realistic?". Pause. Don't proceed without confirmation.
  - **Step 2** — after the researcher's edits (if any) — ask again "OK now?". Only move to Step 3 on an explicit "yes / go."
  - **Step 3** — after fully generating `report.md`: "the report draft is in `4-output/report.md`. This is the **academic version** — to hand it to the stakeholder it still needs to go through `18.5-narrative-adapt`. Say 'adapt it' or edit it by hand first — I'll wait." Pause.
  - With `session_budget: low` — a STOP-handoff after Step 3 (see the "STOP — handoff" section below); 18.5 runs in a new chat.
- **autonomous**:
  - **Step 1** — write `outline.md` yourself.
  - **Step 2** — auto-approve: record in `concerns.md` that "the outline was assembled without the researcher's confirmation (autonomous)"; set `outline_approved: true` yourself with the note `autonomous_approved: true` (the researcher will see it later).
  - **Step 3** — write the full report; in `concerns.md` record where you were worried about quote quality, where the recommendations felt forced. Afterwards — **automatically** run `18.5-narrative-adapt` (this is not an optional step in autonomous).

## Contract with the next stage

The output of `18-report-draft` is the **researcher's draft**, not the final. It contains:
- academically precise wording;
- respondent identifiers `R0X`;
- ranked recommendations with priorities;
- technical metrics where needed;
- quotes that passed the verbatim check.

This draft does NOT go directly to `19-format` — `18.5-narrative-adapt` is mandatory between them; it rewrites the text for the stakeholder (anglicisms, percentages, type labels, names via geography, poetic prose → descriptive-factual tone, "answers to the hypotheses up front" structure).

`18.5-narrative-adapt` refuses to work with a report that lacks `outline_approved: true` in the frontmatter — that means Step 2 was skipped. `19-format` refuses to work with a report that lacks `narrative_adapted: true` in the frontmatter. Both are hard gates.

## After the pass — mandatory (lessons-extraction)

Lessons-extraction has moved to `18.5-narrative-adapt`, because only after the adaptation is the total volume of edits (style + content) visible. If in this skill (`18`) you noticed something methodologically important (e.g. a quote critically garbled during transcription) — record it in `concerns.md` so that `18.5` can pick it up.

The old lessons-extraction section (how it used to work):

1. Read `feedback.md` for the project (the researcher's categorized edits).
2. Compare the key passages of your early drafts in `.system/runs/` or in the history of `4-output/report.md` against the final version — find substantive divergences (what the researcher rewrote, which quotes were removed, which recommendations were reframed).
3. Read `.system/agent-notes.md` — especially the decisions log with methodological forks.
4. Formulate **1–5 short lesson candidates**. Each is one or two lines, a concrete rule, not a methodological essay.
5. In chat with the researcher — briefly (3–5 lines):

   ```
   Here are the edits we made over the course of the project:
   - <category>: <short description>
   - ...

   Lesson candidates for the future:
   1. <lesson>
   2. <lesson>

   Confirm?
   ```

6. On the researcher's confirmation — append to `RESEARCH_PROJECTS_ROOT/_knowledge/lessons.md` in the format from `docs/feedback-loop.md` (`## YYYY-MM-DD — <slug>` + a list with categories and the source project).
7. On a refusal — don't write to `lessons.md`. Record in `.system/agent-notes.md` that it was rejected, so you don't propose the same thing on a restart.

This is a **trigger** you run yourself after `18-report-draft`. Don't wait for "let's close the project" or "collect the lessons" — the researcher may forget, and the material is freshest right now.

For the full context — see `AGENT.md` §12 and `docs/feedback-loop.md`.
