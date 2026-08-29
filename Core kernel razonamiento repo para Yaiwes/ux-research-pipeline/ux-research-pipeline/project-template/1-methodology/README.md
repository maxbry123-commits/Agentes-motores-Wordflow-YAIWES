# 1-methodology

The agent puts drafts here; you edit them.

## What will appear

- `brief.md` — what the stakeholder wants, on what terms, by what deadline, what the definition of done is. Derived from the kickoff meeting or from the materials handed over.
- `questions-and-hypotheses.md` — research questions + hypotheses with testability criteria.
- `guide.md` — the interview guide: blocks, questions, projective techniques, timing. Each block references the research questions.
- `screener.md` — screener questionnaire + criteria and quotas + recruiter instructions.

## How to edit

Plain Markdown. Edits automatically flow into the project's `feedback.md` (the category depends on the type of edit) — material for the retro.

If there are a lot of edits, it's better to tell the agent in words what's wrong and ask it to redo the draft. Otherwise your edits won't be picked up by the context of the later steps.

## When to fill in `questions-and-hypotheses.md`

After the brief is agreed. Once they're ready, copy them into `project-config.yaml` (the `research_questions` field) — the agent needs them for the later coding and analysis steps.
