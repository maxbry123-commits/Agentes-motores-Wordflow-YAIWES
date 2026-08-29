---
name: brief-intake
description: Brief intake with the stakeholder — turns a meeting recording/notes or a free-form description into a structured brief draft. Triggers — "go through the stakeholder meeting", "what does the stakeholder want", an audio file appearing in `0-input/`, or an explicit researcher request. Produces a draft in `1-methodology/brief.md` and, in chat, 2–3 research design options (generative/evaluative, method, sample).
stage: 1.1
status: core
---

# 01-brief-intake

## Why

Translate the stakeholder's business question into a research task. The forks that must be made explicit:
- generative vs. evaluative;
- broad vs. narrow scope;
- what the stakeholder will do with the result.

## Inputs

- Stakeholder meeting recording (`0-input/<name>.mp4|mp3|wav|m4a`) — transcribed via `06-transcribe` if not already transcribed.
- Or a text note in `0-input/<name>.md|txt`.
- (Optional) product context from the researcher's `thoughts.md`.
- (Optional) **the stakeholder's background materials** in `0-input/`: product docs, dashboards, screenshots, links to previous research, business metrics. Always ask (see below).

## Asking for background materials (hard rule)

**After transcribing the stakeholder meeting — always ask the researcher about background materials.** Don't write the brief "blind" from a single meeting recording: product knowledge, numbers, and previous research strongly change the interpretation.

Ask in a single message:

> Before I write the brief — is there anything else on this task I should see? For example:
>
> - product docs or one-pagers from the stakeholder;
> - dashboards or links to metrics they showed or mentioned;
> - previous research on this topic (ours or external);
> - screenshots, diagrams, mockups from the discussion.
>
> If there is — put it in `0-input/` (any format). If not — say "no", and I'll go by the meeting recording I have.

Don't launch the design options until you've received an answer. Silence does not count as "no".

## Outputs

- `1-methodology/brief.md` — a brief draft.
- In chat with the researcher (assistive mode) — a short task summary + 2–3 design options.

### Structure of `brief.md`

```markdown
---
type: brief
client: TODO
date: TODO
status: draft
---

# Brief

## Business question
{{what the stakeholder wants to learn, in their words}}

## What the stakeholder intends to do with this
{{what decision to make, what step to take}}

## The stakeholder's existing hypotheses
- {{hypothesis 1}} — the stakeholder is confident / doubtful
- ...

## Constraints
- Timeline: ...
- Budget: ...
- Access to respondents: ...
- What definitely cannot be asked (NDA, policy): ...

## Out of scope
{{explicitly: what we do NOT research}}

## Definition of Done for the brief
- [ ] research questions formulated
- [ ] hypotheses testable
- [ ] method chosen
- [ ] sample defined
- [ ] timeline agreed
```

## Prompt skeleton

```
You are helping a UX researcher run brief intake with a stakeholder.

Context: a stakeholder meeting recording (transcript below) and the researcher's notes.

Your task: extract from the material the answers to the following questions:
1. What business question lies behind the stakeholder's request?
2. What does the stakeholder intend to do with the research result?
3. What hypotheses do they already have (explicit and implicit)?
4. What constraints are there (timeline, budget, access, political)?
5. What is explicitly out of scope?

Constraints:
- Don't fabricate what the stakeholder didn't say. If there's no data on some point — mark it TODO.
- Don't interpret the stakeholder's words; quote them and mark facts vs. their interpretation.
- If the stakeholder contradicts themselves — note it in a separate "contradictions" block.

After that, propose 2–3 research design options. Each option:
- generative or evaluative;
- method (in-depth / focus / usability / a dozen questions over email — whatever is reasonable);
- sample size and segments;
- approximate timeline;
- what we'll get in answer to the business question (and with what limitations).

Transcript / notes:
{{material}}
```

The full skeleton is inline above (in this SKILL.md) — adapt it directly if customization is needed.

## DoD

- [ ] The brief contains the business question (not a paraphrase, but a formulation).
- [ ] The stakeholder's hypotheses are written out explicitly and marked as "theirs", not "ours".
- [ ] Constraints and out of scope are recorded.
- [ ] In chat — 2–3 design options with rationale.

## Failure modes

- **The stakeholder said "I want everything", and the agent wrote it down.** That's not a task. Force yourself to formulate a concrete, decisive question; if it can't be extracted from the material — flag the researcher: "we need a second clarifying interview with the stakeholder".
- **The business question is mixed with the research question.** "How many people use feature X" is a business question, a metric. Don't formulate it as a research question. RQ is the next step (`02-rq-audit`).
- **An implicit "the stakeholder already knows the solution" is taken on faith.** Often the stakeholder arrives with a ready answer: "we need to rebuild onboarding". Record this as the **stakeholder's hypothesis**, not as an actual RQ.
- **All design options are in-depth interviews.** That's the team's native specialty, but not every question requires in-depth specifically. If the task is about metrics — flag: "this is possibly not our task, quantitative methods are needed".

## Mode behavior

- **assistive**: after generating `brief.md` — pause, in chat 2–3 design options, wait for the researcher's decision.
- **autonomous**: the brief is written, design options are listed in `concerns.md`, the most general reasonable one is chosen, and it moves on. This is a rare case — usually `01-brief-intake` isn't called in autonomous (the brief already exists).
