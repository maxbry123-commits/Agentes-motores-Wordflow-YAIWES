---
name: screener
description: Builds the screener end to end — criteria (must/nice/stop), quotas by segment, the screener questionnaire with anti-gaming questions, and instructions for the recruiter (how to interpret answers, what the red flags are, how to phrase a rejection). Trigger — after RQs and segmentation are agreed. Produces `1-methodology/screener.md` as a single document.
stage: 4.1+4.2+4.3
status: core
---

# 05-screener

## Why

Combines three substages (4.1+4.2+4.3) into one artifact. They are tightly linked: criteria determine the questions, the questions determine the recruiter's instructions.

The main risk of a screener is **self-selection bias**: respondents "guess" the desired profile and adjust their answers. Anti-gaming is the main task.

## Inputs

- `project-config.yaml` — the `segments` field (if filled in).
- `1-methodology/brief.md` — for quotas and context.
- `1-methodology/questions-and-hypotheses.md` — to understand which experience is critical.

## Outputs

- `1-methodology/screener.md`.

### Structure

```markdown
---
type: screener
total_quota: TODO
segments_count: TODO
status: draft
---

# Screener

## Criteria

### MUST (without these — stop)
- {{criterion}} — how it's checked in the questionnaire: question {{N}}.

### NICE (priority, but not a blocker)
- {{criterion}}

### STOP (exclusionary)
- {{criterion}} — for example, works for a competitor, professional tester, took part in our research in the last 3 months.

## Quotas

| Segment | Quota | Stop-criterion | Priority |
|---|---|---|---|
| {{name}} | {{N}} | {{what makes them invalid}} | high/medium/low |

## Questionnaire

> N — the sequential number of the question for references from the criteria.

### 1. {{behavioral question}}
- type: behavioral
- options: [...] / open
- conceals: {{which must/nice/stop it checks}}

### 2. {{paraphrase question for antigaming}}
- type: gating-paraphrase
- options: [...]
- checks consistency with question 1.

### 3. {{question about opt-out}}
- "If you were offered to skip some stage — how OK is that for you?"
- type: trap-for-must-participate

(pattern: for each MUST criterion — two questions, one direct and one behavioral paraphrase; consistency of answers = validity)

## Recruiter instructions

### How to interpret answers
- Questions 1 and 2 should be consistent. If not — reject or run an additional check.
- Question 5 is open. If the answer is shorter than 1 sentence — a clarifying follow-up call is needed.

### Red flags
- The respondent knows industry jargon in the questionnaire (like "UX", "touchpoint") — possibly a professional respondent or tester.
- Answers a behavioral question too smoothly (sounds like it's from a textbook).
- A perfect profile across all segments (no contradictions) — a reason to call and clarify.

### Rejection wording
> "Thank you for your interest. Unfortunately, this time we're looking for participants with different experience. May we contact you in the future on other topics?"

(never: "you're not a fit for us", "you didn't pass")
```

## Prompt skeleton

```
You are helping a UX researcher build a screener for recruiting respondents.

Brief:
{{insert}}

Segments and quotas:
{{insert from project-config.yaml}}

Research questions:
{{insert}}

Task:
1. Split criteria into MUST / NICE / STOP. For each — which questionnaire question checks it.
2. Build a questionnaire (5–10 questions) — each MUST criterion is checked by two questions (a direct one and a behavioral paraphrase) for anti-gaming.
3. Write recruiter instructions: how to interpret answers, red flags, rejection wording.
4. Flag: where self-selection is easy to fake (explicit indicators), where an additional call helps.

Anti-gaming rules:
- Don't put what you're looking for in the question wording ("Do you use in-app payments regularly?" — yes, of course). Use the indirect: "When did you last make a purchase through the app? Describe what you bought".
- Behavioral > attributive.
- Trap questions (for example, negative options for "socially desirable" behaviors) — where appropriate.
```

## DoD

- [ ] Each MUST criterion is checked by at least two questions.
- [ ] Quotas are filled in and realistic (not "6 from each, 30 total" when the budget is for 12).
- [ ] Stop-criteria are explicit.
- [ ] The recruiter instructions contain the rejection wording.

## Failure modes

- **Direct questions instead of behavioral ones.** "Do you search often?" — easily gamed. "When did you last search for something in the app? What did you search for? Did you find it?" — verifiable.
- **Overdoing the questionnaire length.** >12 questions — high drop-off. Cut it.
- **Stop-criteria forgotten.** The most common — "worked in professional UX/UI development or testing". A professional respondent = spoiled data.
- **"A fit on all criteria" — is that normal?** In real life there are no perfect profiles. A respondent who's too smooth = suspicion.

## Mode behavior

- **assistive**: pause, in chat — what in the questionnaire is easy to game, whether additional questions are needed.
- **autonomous**: anti-gaming concerns — in `concerns.md`.
