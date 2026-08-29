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

{{2–3 paragraphs: the gist in 30 seconds of reading. Business question → key findings → main recommendations. No "the research showed that" — be concrete.}}

## About the project

- **Business question**: {{from the brief, reformulated}}.
- **Method**: {{N in-depth interviews with {{segments}}}}, {{N}} hours total.
- **Period**: {{dates}}.
- **Limitations**: {{what this method does not cover}}.

## Research questions and short answers

| RQ | Answer |
|---|---|
| RQ1: {{question}} | {{1–2 sentences}} |
| RQ2: {{question}} | {{1–2 sentences}} |

## Key findings

> Ranked by strength of the evidence base.

### F1: {{one-line statement}}

{{An extended paragraph with reasoning. Not a retelling of the data, but a conclusion.}}

**Evidence:**
- > "{{verbatim}}" — {{R0X, segment}} `[mm:ss]`
- > "{{verbatim}}" — {{R0Y, segment}} `[mm:ss]`
- {{N respondents in the sample mentioned it; distribution across segments}}.

**Limits of applicability:** {{where it doesn't hold; in which segment the opposite is true}}.

**Confidence:** medium / high.

### F2: ...

(5–7 findings)

## Typology (optional)

{{If one was built and passed the anti-pattern check. See `3-analysis/typology.md`.}}

## Paradigm model (optional)

{{If relevant for the report. Can be an image from the canvas or a textual description.}}

## What we did not find (although we looked)

- **Hypothesis H{{X}}** was not supported: {{which data argues against it}}.
- {{Aspect Y that we expected to see but that didn't surface — possibly a guide or sample artifact}}.

## New hypotheses for the next study

- {{a pattern not anticipated by the original brief; needs quantitative verification or additional interviews}}.

## Recommendations `[draft]`

> **Recommendations are a draft.** The final version needs to be discussed jointly with the product manager and designer.

### R1 — based on F1
- **What we do**: {{a concrete action, not "improve the UX"}}.
- **Who it's addressed to**: {{the onboarding / search / etc. team}}.
- **Why**: reference to F1.
- **Expected effect**: {{what will change; ideally a measurable metric}}.
- **Priority**: high / medium / low.
- **Depends on**: {{what needs to happen first}}.

### R2 — ...

## Methodological caveats

- {{sample limitations: size, diversity of segments}}.
- {{method limitations: in-depth gives no counts, doesn't work for rare events}}.
- {{what needs additional verification quantitatively or via another method}}.

## Appendices

- Full transcripts: `2-interviews/` (internal access).
- Respondent maps: `3-analysis/respondents/`.
- Categories and axes: `3-analysis/_categories.md`.
- Paradigm model: `3-analysis/model.canvas`.
- Saturation map: `3-analysis/matrix.xlsx`.
- Interview guide: `1-methodology/guide.md`.
- Screener: `1-methodology/screener.md`.
