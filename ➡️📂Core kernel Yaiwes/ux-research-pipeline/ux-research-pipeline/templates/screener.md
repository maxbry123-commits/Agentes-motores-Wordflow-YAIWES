---
type: screener
total_quota: TODO
segments_count: TODO
status: draft
---

# Screener

## Selection criteria

### MUST (without them — stop)
- {{criterion 1}} — checked in the questionnaire: question {{N}} + behavioral paraphrase: question {{M}}.
- {{criterion 2}} — ...

### NICE (priority, not a blocker)
- {{criterion}}

### STOP (exclusions)
- Works for a competitor / has worked professionally in UX/UI/testing
- Took part in our research within the last 3 months
- {{other exclusions}}

## Quotas by segment

| Segment | Quota | Stop criterion | Priority |
|---|---|---|---|
| {{name}} | {{N}} | {{what makes them invalid}} | high/medium/low |
| {{name}} | {{N}} | ... | ... |

**Total**: {{N}} respondents.

## Questionnaire

> Logic: for each MUST criterion — two questions, one direct and one behavioral paraphrase. Consistency of answers = validity.

### 1. {{Behavioral question}}
- type: behavioral
- options: [...] / open
- checks: MUST criterion "{{X}}".

### 2. {{Control paraphrase}}
- type: gating-paraphrase
- options: [...]
- checks consistency with question 1.

### 3. {{Demographics}}
- type: demographic
- options: [...]

### 4. {{Experience with the product}}
- type: experience
- options: [...]

### 5. {{Trap question}}
- "Do you enjoy being asked to talk about your experience?" (negative trap, checks that the respondent isn't just chasing any study for the money)
- type: trap

### 6. {{Open descriptive question}}
- "Describe the last time you did X" — type: open. If the answer is shorter than one sentence, a follow-up call is needed.

(6–10 questions total; more means high drop-off)

## Instructions for the recruiter

### How to interpret answers
- Questions 1 + 2 should be consistent. If not — reject or do an additional check by phone.
- Question 5 — if the respondent enthusiastically confirms "yes, I love it" — that's a gray zone (a savvy respondent or a sincere one?). Call them.
- Question 6 — if the answer is too short or too polished — call them, ask for specifics.

### Red flags
- The respondent uses industry jargon in the questionnaire ("UX", "touchpoint", "conversion").
- A perfect profile across all segments — no contradictions.
- Experience with the product is "I actively use it every day, have for 5 years" while the answer to question 6 is "don't remember exactly, something like that..."

### Wording for a rejection
> "Thank you for your interest. Unfortunately, this time we're looking for participants with a different background. May we reach out to you in the future on other topics?"

(never: "you're not a fit for us", "you didn't pass", "you don't qualify")

### After recruitment
- Hand off to the researcher: respondent ID + segment + fragments of the answer to question 6 + any doubts.
- Don't pass PII into a shared chat — only through a secure channel.
