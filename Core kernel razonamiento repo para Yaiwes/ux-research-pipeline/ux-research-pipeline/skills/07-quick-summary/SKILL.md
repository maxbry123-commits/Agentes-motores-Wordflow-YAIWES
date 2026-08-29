---
name: quick-summary
description: Produces a short interview summary for the team (3–5 key points + strong quotes with timecodes). Trigger — an interview transcript appears in `2-interviews/<name>.txt` (runs automatically after `06-transcribe`). Produces `<name>-summary.md` next to the transcript. Can be pasted into the team chat as is.
stage: 5.3
status: core (auto)
---

# 07-quick-summary

## Why

The team learns interview results 2–3 weeks later, once the report is ready. That's too late. A quick summary is a way to convey 80% of the useful knowledge within 30 minutes of the interview.

## Trigger

A transcript appears in `2-interviews/<name>.txt` (by any means — after `06-transcribe` or placed there manually by the researcher).

**Do it automatically, don't ask.** If the researcher doesn't want it — they'll say "don't make a summary for interview X."

## Inputs

- `2-interviews/<name>.txt` — transcript with timecodes.
- (Optional) the researcher's notes, if there's a `<name>-notes.md` alongside.
- `1-methodology/questions-and-hypotheses.md` — to structure the summary by research question.

## Outputs

- `2-interviews/<name>-summary.md`.

### Structure

```markdown
---
type: quick_summary
respondent: TODO
date: TODO
duration_min: TODO
---

# Interview summary {{name}} — for the team

> 3–5 minute read. Full transcript — in `2-interviews/<name>.txt`. Analysis — in `3-analysis/respondents/<name>.md` (appears after coding).

## Who the respondent is

{{Segment, ~age, ~experience with the product — no PII}}

## TL;DR

{{1–2 sentences of the main point}}

## 3–5 key points

1. **{{point}}** — briefly why. Quote:
   > "{{verbatim}}" `[mm:ss]`

2. **{{point}}** — ...

## What was surprising / contradicts expectations

{{1–3 observations}}

## What went beyond the guide (but is interesting)

{{spontaneous topics}}

## Relevant to our research questions

| RQ | What we learned |
|---|---|
| RQ1 | ... |
| RQ2 | ... |

## ⚠️ Where the data is thin

(where the interview didn't give clarity — worth probing in the next ones)
```

## Prompt skeleton

```
You are producing a quick summary of an interview for a team of UX researchers.

Transcript:
{{insert `<name>.txt`}}

Researcher's notes (if any):
{{insert}}

Project research questions:
{{insert}}

Task:
1. Pick 3–5 key points. "Key" means about the product, not about methodology.
2. For each — a verbatim quote with a timecode. The quote must exist in the transcript word for word.
3. Note what was surprising (contradicts expectations).
4. Note what went beyond the guide (spontaneous topics).
5. Make a table mapping each RQ → a brief answer from this interview.
6. If the data is thin anywhere — flag it explicitly.

Constraints:
- Do NOT use respondent PII (name, phone, home city). Only aggregated demographics.
- Quotes — verbatim, checked for existence in the text.
- Don't over-interpret — this is a summary, not analysis. Analysis will be in `3-analysis/respondents/<name>.md`.
- Do NOT use percentages ("50% said…") — this is one interview.
```

## DoD

- [ ] 3–5 points with quotes.
- [ ] Each quote checked verbatim against the transcript.
- [ ] No PII mentioned.
- [ ] Length — one screen at a comfortable font size (~250–400 words).

## Failure modes

- **Too many points (>7).** That's no longer a quick summary. Trim it.
- **The quote wasn't found verbatim** — leave it as a paraphrase without quotation marks; don't put a paraphrased version in quotes.
- **"The respondent said that 70% of people…"** A respondent may say this (it's their opinion), but we don't cite it as fact. Leave it as "respondent's perception" with a note.
- **Too much PII in a quote** ("I work at X, my wife is …"). Don't quote that; use a paraphrase.

## Mode behavior

- **assistive**: after generation — a short chat message: "summary for R0X is ready, copy it into the team chat (`<path>`)." No pause.
- **autonomous**: write it and move on, no message.
