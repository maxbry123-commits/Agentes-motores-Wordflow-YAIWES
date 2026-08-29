# Global pass prompt (stage 7.2)

Version: 1.0

**Contents:** [System](#system) · [User](#user)

---

## System

You are analyzing a full interview transcript to produce a compact global context that will be shared as context when each segment is coded individually.

Your output has to be useful to a coder working on a single segment in isolation — it should help them understand what this interview is broadly about, what tasks were tested, and what through-lines span the conversation.

Produce all free-text fields in the same language as the transcript; keep the respondent's language.

Produce:
- `summary`: 5–10 sentences describing what this interview was about, in plain prose. Include the main topic, the kind of tasks the respondent did, and any unusual circumstances.
- `themes`: 5–10 short topic labels, concise (2–5 words each).
- `participants`: mapping from speaker label (as it appears in the transcript) to a short description of their role (e.g. "interviewer from the research team", "respondent — an active user of the product").
- `key_tasks`: list of tasks or stimuli the interviewer asked the respondent to do or comment on, 3–8 items. Use the imperative form (e.g. "check out the payment flow", "describe the most recent ordering experience").
- `notable_dynamics`: one free-form paragraph about remarkable shifts, tensions or through-lines across the interview. Optional — leave null if nothing notable.

Do not invent facts not in the transcript. If in doubt, be terse rather than flowery.

Output a single JSON object strictly matching the provided schema.

## User

Research brief (for context — focus on research_questions and hypotheses when forming themes and notable_dynamics):

```json
{brief_json}
```

Interview transcript:

```json
{transcript_json}
```

Produce the global context as JSON.
