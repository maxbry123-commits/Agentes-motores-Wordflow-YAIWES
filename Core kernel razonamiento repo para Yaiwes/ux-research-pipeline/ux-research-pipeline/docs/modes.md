# Modes: assistive vs autonomous

This is about where each mode applies. For practice, see `getting-started.md`.

## TL;DR

| | assistive | autonomous |
|---|---|---|
| Who decides | The researcher, after each substantive step | The agent runs through, the researcher reviews at the end |
| Duration | Slow, like a normal study | Fast |
| Where it works | Any project | Narrow scope (see below) |
| Final gate | The researcher, after each step | The researcher **mandatorily**, before anything goes out |
| Applicable to stakeholder conclusions | Yes | **Only** after human review |

## assistive — the main mode

The default. Use it if:
- The study is being done from scratch.
- The stakeholder is waiting for results and will make decisions based on them.
- The topic is new to you or the team.
- Segmentation and quotas aren't dialed in yet.

What it gives you:
- Control over methodological forks (generative vs evaluative, number of interviews, typology).
- Early catching of methodological mistakes.
- Collection of `feedback.md` — fuel for improving prompts.

Agent behavior:
- After each substantive artifact (brief, research questions, guide, screener, coding, key findings, report) — a pause, a short summary in chat, and a wait for your reaction.
- Actively flags things: "you forgot about X," "the data is thin here," "there's a contradiction here."
- Writes intermediate artifacts to `3-analysis/` incrementally — open Obsidian at any time and you'll see a live picture.

What it costs:
- Time. The full pipeline runs over several weeks or months, like a normal study.

## autonomous — agent-first with a final human gate

Applicable to a narrow set of scenarios:

### A. Auditing an external agency

"An agency ran 12 interviews and sent the transcripts and a PDF report. There's no time for a full re-check — I need to understand within a day what to trust, what not to, and what they missed."

The agent:
1. Runs the transcripts through its own pipeline (stages 7–9).
2. Compares its findings with what's in their report.
3. Flags: what is confirmed, what they over-interpreted, what they missed.

### B. Desk research

"I want to understand within a day what we already know about topic X before taking on a new study."

Fully autonomous — no confidentiality risks, the conclusions are reference-grade.

### C. Draft of key findings on existing transcripts

"The transcripts exist, the coding exists, there's no time to refine the conclusions myself — I need a draft to edit."

The agent provides a draft of key findings and recommendations. The researcher sits down and rewrites it.

## Where autonomous does **not** work

Hard limit.

### Brief intake with a stakeholder

The stakeholder doesn't know what they want. Translating a business question into a research question is dialogic work. Here an autonomous agent can only generate platitudes, which is worse than nothing.

### Methodological forks

"Build the guide for a generative or evaluative study," "how big a sample to take," "one segment or three," "do we need projective techniques" — these are methodological decisions grounded in the team's knowledge and the product context. The agent will make a "reasonable default choice," and in a meaningful share of cases it will be harmful.

### Final recommendations to stakeholders

A recommendation = the jump from "finding" to "what we do about it." That jump requires knowledge of the product context, politics, team history, and past failures. The agent won't make it.

### Confirming null hypotheses

Any "respondents have no problem X" can't be trusted automatically. Too often the agent confuses "wasn't mentioned" with "isn't a problem."

## The final human gate in autonomous

A hard rule, not configurable:

> A study's final artifact **does not go out** (to a stakeholder, into a public presentation, into open-access wiki) **without being read by the researcher**.

What must be in `4-output/handoff.md` by that point:
- A list of all generated artifacts.
- `concerns.md` — all methodological compromises and the "I'm not sure" spots.
- A list of quotes tied to timecodes.
- An explicit disclaimer: "draft, requires review."

If `handoff.md` is empty or shallow — don't release it. File an issue or ask for a re-run.

## Mixed mode is not supported in v1

Earlier versions discussed a config like `mode_per_stage: ...`. We've decided to defer it to v2. For now — fully assistive **or** fully autonomous per project.

If midway through a project you want to switch — change `mode:` in `project-config.yaml` and continue. The agent will pick it up. But it's not recommended: it's easy to lose track of which artifacts went through review and which didn't.
