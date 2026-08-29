---
name: guide-builder
description: Builds the interview guide and immediately audits it for leading questions, double-barreled items, and overly cognitively loaded wording. Trigger — after RQs are agreed. Each guide block is explicitly mapped to one or more RQs. Produces `1-methodology/guide.md` with timing, question types (open / probe / projective), and stimuli.
stage: 3.1+3.2
status: core
---

# 04-guide-builder

## Why

The guide is the main artifact before data collection. Common problems:
- **Leading**: "Is feature X convenient to use?" (it presupposes that it's convenient).
- **Double-barreled**: "Is it clear and convenient to you?" (two questions in one).
- **Cognitively overloaded**: "Recall how three weeks ago you…".
- **Doesn't cover an RQ**: the block exists but leads to answering no RQ.

The skill generates the guide **and immediately audits it**.

## Inputs

- `1-methodology/questions-and-hypotheses.md`.
- (Optional) `1-methodology/desk-research.md` — for context.
- (Optional) `1-methodology/guide.md` from a past study on a similar topic — as a reference.

## Outputs

- `1-methodology/guide.md`.

### Structure

```markdown
---
type: interview_guide
duration_min: 60
status: draft
last_updated: TODO
---

# Interview guide

> Total: ~60 minutes.

## 0. Warm-up (2 min)
- {{question — type: open}}

## 1. {{Block A}} (~10 min) — RQ1, RQ2
- {{question}} — type: open
- {{probe}} — type: probe
- {{stimulus}} — type: stimulus, attached: …

## 2. {{Block B}} (~15 min) — RQ3
...

## N. Closing questions (3 min)
- {{summary question}}
- {{what we forgot to ask}}

## Mapping of blocks → RQ

| Block | RQ | Hypotheses | Type |
|---|---|---|---|
| 1 | RQ1, RQ2 | H1 | core |
| 2 | RQ3 | H2 | core |
| 3 | — | — | warmup |

## Wording audit

| Question | Note |
|---|---|
| "Is feature X convenient to use?" | leading — presupposes "convenient". Replace with "Tell me how you use X. What was easy about it, what was hard?" |
| ... | ... |
```

## Prompt skeleton

```
You are helping a UX researcher build an interview guide.

Research questions:
{{insert}}

Hypotheses:
{{insert}}

Task:
1. Build a guide of 5–8 blocks. Each block maps to 1+ RQ.
2. Use a mix: open questions, probes, projective techniques (where appropriate), stimuli (if the RQ requires a reaction to a specific artifact).
3. Run an audit:
   - leading questions (contain a presumed answer);
   - double-barreled (two questions in one);
   - cognitively overloaded;
   - blocks with no mapping to an RQ;
   - RQs not covered by any block.

Rules:
- Don't use the words "convenient", "clear", "easy", "like" in the wording of the question itself — these are closed presuppositions. Use "tell me how", "describe", "recall the last time you".
- A probe is not the same question in other words. A probe deepens: "why exactly that way?", "what came before this?", "what would you want instead?".
- Projective: "imagine the system is a character. What's their personality?". Use it where a direct question doesn't work (values, emotions, identity).
```

The prompt skeleton above is inline in this SKILL.md — there is no separate prompt file.

## DoD

- [ ] Each block has a mapping to at least one RQ.
- [ ] All RQs are covered by at least one block.
- [ ] The audit is done, leading/double-barreled notes are added.
- [ ] Total timing is stated and realistic (not 90 minutes for a 60-minute interview).
- [ ] The "closing questions" section exists (what we forgot to ask, what to add).

## Failure modes

- **The guide = a list of RQs.** No, an RQ is what we want to learn, the guide is how we ask the respondent for it. These are different things.
- **No probe questions.** Open questions without follow-ups yield shallow answers.
- **Too many projective techniques.** They're good, but not for every block. 1–2 per guide is enough.
- **Technical terms in the wording.** "Tell me how you use the CTA button" — the respondent doesn't know what a CTA is. Replace with a concrete visual description.

## Mode behavior

- **assistive**: after generation — pause, in chat the gist of the audit (top 3 problems) + an offer to read it.
- **autonomous**: the guide is written, the audit goes in the guide itself, serious problems go in `concerns.md`.
