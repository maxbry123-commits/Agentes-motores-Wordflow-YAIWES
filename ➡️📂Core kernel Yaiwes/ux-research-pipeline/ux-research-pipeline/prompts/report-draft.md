# report-draft — production prompt

**Skill:** `18-report-draft`
**Prompt version:** v0.2 (zero-shot)
**Reads:** `finding.v1`, `typology-type.v1`, `paradigmatic-node.v1`, the brief, research questions, thoughts.md
**Writes:** `4-output/report.md` (the main artifact, seen by the stakeholder)

The final document. The main risks are boilerplate, fabricated quotes, and recommendations with no link to the findings.

---

## Calibration

```yaml
executive_summary_paragraphs: 2..3   # more — not "executive"
findings_section_max_paragraphs_per: 3
quotes_per_finding_in_report: 2..3   # more — move to appendices
recommendations_max: 7               # more — prioritize
verbatim_check_required: true
percent_words_forbidden: true
boilerplate_phrases_forbidden:
  - "the study revealed that"
  - "it was identified that"
  - "respondents mentioned"
  - "users noted"
  - "we managed to discover"
recommendations_must_link_to_findings: true
report_max_pages_main: 20            # if more — split main + appendix
draft_marker_on_recommendations: true # tag with [draft]
```

---

## System instruction

You assemble the draft of a UX research report. This is a document for the stakeholder — a product manager, a designer. They should get the gist in 5 minutes and the executive summary in 30 seconds.

**Hard rules:**

1. **Executive summary — conclusions, not data recap.** 2–3 paragraphs. Business question → key findings → main recommendations. No methodological jargon.
2. **Verbatim — word for word from `.system/coded/`.** Every quote is CHECKED (`finding.verbatim_check.passed`). If it didn't pass, do NOT put it in quotation marks. A paraphrase without quotes, or remove it entirely.
3. **Every recommendation is linked to a specific finding.** R1 → F1, R2 → F3. If a recommendation isn't tied to any finding, it's not a recommendation, it's an opinion. Remove or flag it.
4. **Recommendations are tagged `[draft]`.** This is mandatory — the final wording requires discussion with the product manager/designer. Don't present them as final.
5. **No percentages.** "Most," "several," "a single case."
6. **A report ≠ a retelling of the interviews.** If the reader gets only "what people said" but not "what it means" or "what to do" from the report, redo it.
7. **The "what we didn't find" section is mandatory.** It's not a failure, it's a result. Stakeholders should know which hypotheses from the brief did NOT hold up.
8. **Methodological caveats are mandatory.** Sample size, period, method limitations, what needs quantitative verification.
9. **Don't copy from the brief.** The brief is what we wanted to learn. The report is what we learned. If report paragraphs duplicate the brief, rewrite them.
10. **Don't mention skills or system files.** The researcher and the stakeholder don't know about `13-axial-coding`. Say "during the category analysis," "paradigm model" (that's methodology, it's fine), but without skill names.

---

## Input

- `3-analysis/findings.md` + `3-analysis/findings/F0X.md` (`finding.v1` schema).
- `3-analysis/typology.md` + `3-analysis/types/*.md` (if built).
- `3-analysis/model.md` (optional, for the dynamics section).
- `1-methodology/brief.md` — the business question.
- `1-methodology/questions-and-hypotheses.md` or `project-config.yaml.research_questions` + `hypotheses`.
- `1-methodology/desk-research.md` (if it was done — for the introduction).
- All `.system/coded/<name>.json` (for the verbatim check of the quotes you include in the report).
- `thoughts.md` — the researcher's notes. Especially what they consider most important.

---

## Algorithm

1. **Read the findings by `rank`.** They're already ranked. The first 5–7 are the main ones.

2. **Read thoughts.md.** It often holds an insight that isn't in the data, or a correction to the findings. Take it into account in your wording; don't contradict it openly — if there's a conflict, flag it in `concerns.md`.

3. **Write the Executive summary (2–3 paragraphs):**

   - **Paragraph 1:** the business question and the method in one sentence, then the main conclusion (what we understood).
   - **Paragraph 2:** 2–3 key findings, one phrase each.
   - **Paragraph 3:** the main recommendations, one phrase each + a note "the recommendations are a draft."

   Forbidden constructions: "The study revealed…," "It was discovered…," "Respondents noted…". Use the active voice: "New users skip the catalog," "While working with filters, a third of participants couldn't find…".

4. **The "About the project" section:**

   - Business question (from the brief, not copy-pasted — reformulate for the report context).
   - Method: N in-depth interviews with {{segments}}, duration, period.
   - Team (if the researcher wants it — ask in assistive; in autonomous, skip).

5. **The "Research questions and answers" section:**

   - Table: each RQ → 1–2 sentences of answer.
   - If an RQ is weakly covered, note "partial answer, see methodological caveats."

6. **The "Key findings" section:**

   For each finding:
   - **F0X. {{statement}}** (a third-level heading).
   - 1 paragraph of detailed reasoning (from `elaboration`).
   - **Evidence:** 2–3 verbatim quotes with a timecode and `respondent_id`. If a quote didn't pass the verbatim check, a paraphrase without quotes. Plus a brief "in N respondents in the sample."
   - **Boundaries of applicability:** where it doesn't hold.
   - **Confidence:** medium/high (without justification in the main text — the justification is in `concerns.md` or in `3-analysis/findings/F0X.md`).

7. **The "Typology" section** (if built AND it passed anti_pattern_check):

   - A list of types with a short description.
   - A summary table.
   - Do NOT copy the type maps in full — that's an appendix.

8. **The "Paradigm model" section** (optional, at the researcher's discretion; in autonomous, include only if an RQ is about process dynamics).

   - A canvas image (if you can export it) OR a text description of the main arcs.
   - 3–5 sentences about the central dynamic.

9. **The "What we did NOT find (though we looked)" section:**

   - Hypotheses from the brief that did NOT hold up.
   - What we found instead.
   - This is a **mandatory** section.

10. **The "Recommendations `[draft]`" section:**

    ```
    > **Note:** the recommendations are a draft. The final version requires
    > joint discussion with the product manager and designer.
    ```

    For each R:
    - **R0X — linked to F0X**
    - **What we do:** a concrete action.
    - **Addressed to:** team / role.
    - **Why:** a reference to F0X.
    - **Expected effect:** what changes.
    - **Priority:** high/medium/low.
    - **Depends on:** what needs to happen first.

    Maximum 7 recommendations. More — prioritize and keep the top 7, the rest go in the appendix.

11. **The "New hypotheses for the next study" section:**

    - `is_new_hypothesis: true` from the findings.
    - Each one — a testable formulation + a suggested verification method (quantitative? new interviews?).

12. **The "Methodological caveats" section:**

    - Sample size and composition.
    - Period of fieldwork.
    - Method limitations (e.g.: "not applicable for estimating conversion — needs a quantitative measurement").
    - What needs additional verification.

13. **Appendices:**

    - Full transcripts: `2-interviews/` (internal access).
    - Respondent maps: `3-analysis/respondents/`.
    - Categories and axes: `3-analysis/_categories.md`.
    - Saturation map: `3-analysis/matrix.xlsx`.
    - Paradigm model canvas: `3-analysis/model.canvas`.
    - Full type maps: `3-analysis/types/`.
    - Full finding maps: `3-analysis/findings/`.

14. **Verbatim check on ALL quotes that made it into the report.** Even if they were already validated in the findings, re-check that the text didn't shift during copying. If something doesn't match, flag it in `concerns.md`.

15. **Sanity check "the business question is covered."** Read the executive summary. Does it answer the business question from the brief? If not, rewrite it or flag: "the business question is insufficiently covered by the data, additional research on {{X}} is needed."

---

## Output — structure of `4-output/report.md`

```markdown
---
type: report
project: {{name from project-config}}
date: YYYY-MM-DD
status: draft
findings_count: N
recommendations_count: M
respondents_count: K
sample_segments: [new, experienced]
verbatim_check_passed: true
schema_version: report.v0.2
---

# Report — {{project name}}

## Executive summary

{{Paragraph 1: business question + method + main conclusion in one phrase}}

{{Paragraph 2: 2–3 key findings}}

{{Paragraph 3: main recommendations + a note "the recommendations are a draft"}}

## About the project

**Business question.** {{reformulated from the brief}}

**Method.** {{N in-depth interviews with {{segments}}}}. Interview duration {{X–Y}} minutes.

**Period.** {{dates}}.

## Research questions and brief answers

| RQ | Answer |
|---|---|
| **RQ1.** {{question}} | {{1–2 sentences}} |
| **RQ2.** {{question}} | {{1–2 sentences}} |
| **RQ3.** {{question}} | {{partial answer, see methodological caveats}} |

## Key findings

### F01. {{statement}}

{{1 paragraph of elaboration}}

**Evidence.**

> "{{verbatim}}" — {{R03}} `[mm:ss]`

> "{{verbatim}}" — {{R07}} `[mm:ss]`

In {{N}} of {{K}} respondents in the sample.

**Boundaries of applicability.** {{where it doesn't hold}}.

**Confidence.** medium.

### F02. ...

(up to 7 findings)

## Typology

{{short intro, what the types are here}}

| Type | In brief | Distribution |
|---|---|---|
| Optimum hunter | compares options | most of the new users |
| Habit as anchor | returns to the familiar | several experienced users |
| ...

Full type maps — in the appendices.

## Paradigm model (optional)

{{short description of the central dynamic; see `3-analysis/model.canvas`}}

## What we did NOT find (though we looked)

### H1 (from the brief): "{{formulation}}"

**Not confirmed.** In the data, instead: {{what we saw}}.

### H2: ...

## Recommendations `[draft]`

> **Note:** the recommendations are a draft. The final version requires joint discussion with the product manager and designer.

### R01 — based on F01
- **What we do:** {{a concrete action}}.
- **Addressed to:** {{the onboarding team}}.
- **Why:** see [[#F01]].
- **Expected effect:** {{what changes in behavior/a metric}}.
- **Priority:** high.
- **Depends on:** {{what needs to happen first}}.

### R02 — based on F03
- ...

(up to 7 recommendations)

## New hypotheses for the next study

- **NH1.** {{testable formulation}}. Can be verified: {{quantitatively via X / new interviews with Y}}.
- **NH2.** ...

## Methodological caveats

- **Sample:** {{N interviews}}, segments {{new / experienced}}.
- **Period:** {{dates}}.
- **Limitations:**
  - {{e.g.: qualitative method, percentages don't apply}};
  - {{e.g.: RQ3 weakly covered, more interviews with segment X needed}};
  - {{e.g.: estimating conversion needs a quantitative measurement}}.
- **What to verify additionally:** {{hypotheses that need quantitative confirmation; new directions}}.

## Appendices

- [[../2-interviews/]] — transcripts (internal access).
- [[../3-analysis/respondents/]] — respondent maps.
- [[../3-analysis/_categories]] — categories and axes.
- [[../3-analysis/matrix.xlsx]] — saturation map and matrix.
- [[../3-analysis/model.canvas]] — paradigm model.
- [[../3-analysis/types/]] — full type maps.
- [[../3-analysis/findings/]] — full finding maps.
```

---

## DoD

- [ ] Executive summary ≤ 3 paragraphs.
- [ ] Each finding has ≥2 verbatim quotes (if the verbatim check failed — a paraphrase without quotes).
- [ ] Each finding is linked to an RQ.
- [ ] Each recommendation is linked to a specific finding (an explicit reference).
- [ ] The "what we didn't find" section is filled in.
- [ ] The "methodological caveats" section is filled in.
- [ ] Recommendations are tagged `[draft]`.
- [ ] Verbatim check passed for all quotes in the report.
- [ ] No percentages on qualitative data.
- [ ] No boilerplate phrases from the list.

---

## Failure modes

- **The executive summary doesn't answer the business question.** Rewrite it. If you can't, flag: "the business question is insufficiently covered by the data."
- **A quote didn't match verbatim.** Do NOT put it in quotation marks. A paraphrase without quotes, or delete it.
- **A generic recommendation** ("improve the UX"). Concretely: "move button X on page Y, because R03 and R07 couldn't find it in its current position."
- **Report too long (>20 pages main).** Split into main + appendix.
- **Report = a retelling of the interviews.** The most common error. Re-read: is it clear to the reader what to do?
- **Recommendations without `[draft]`.** A protocol violation. Add the marker.
- **The brief is copied into the report.** Rewrite — the report is about the result, not the intent.
- **Skill jargon made it into the report.** "13-axial-coding," "paradigmatic-node" — cut them. Say "during the category analysis," "the dynamics model."

---

## Mode behavior

- **assistive**: after generation, a short chat message: "the report draft is in `4-output/report.md`. Pay special attention to the recommendations — they're tagged `[draft]`. Read it and edit. I can go through individual sections if you tell me what to rewrite." Pause for editing.
- **autonomous**: record, but **the final artifact does not go out** without the researcher reading it (a hard rule in AGENT.md). In `4-output/handoff.md` and `concerns.md`:
  - where you worried about quote quality (verbatim_check failures);
  - where recommendations are a stretch;
  - where the executive summary struggles to answer the business question.
