---
name: key-findings
description: The main final analysis artifact — 5–7 key findings that answer the research questions. Merges 8.4 (evidence per hypothesis), 8.9 (new hypotheses), and 8.10 (key findings). Trigger — after `13-axial-coding`, `14-paradigmatic-model`, `15-disconfirm-triangulate`. Each finding is pinned to at least N respondents and M quotes, with an explicit "so what?" for the product. Catches data recap masquerading as conclusions.
stage: 8.4+8.9+8.10
status: core
---

# 17-key-findings

## Why

This is the most visible artifact of the study — what the stakeholder and the team will actually read. The main pitfalls:
- **Data recap instead of conclusions.** "Respondents mentioned onboarding N times" is not a finding.
- **Unranked.** 12 findings of equal weight = useless for the product.
- **No explicit implication.** "Respondents dislike onboarding" — so what?

## Trigger

After `13-axial-coding`, `14-paradigmatic-model`, `15-disconfirm-triangulate`.

May be invoked earlier for a draft (after `draft_findings_after_n_interviews` interviews, default 5) — but the final version only after the full analysis.

## Inputs

- `3-analysis/_categories.md`.
- `3-analysis/model.md`.
- `3-analysis/_disconfirms.md`.
- `3-analysis/_triangulation.md`.
- `3-analysis/typology.md` (if built).
- All `.system/coded/*.json`.
- `project-config.yaml` — research_questions, hypotheses.
- `thoughts.md` — the researcher's notes.

## Outputs

- `3-analysis/findings/F0X.md` — one Markdown card per finding. Template in `prompts/key-findings.md`.
- `3-analysis/findings.md` — a summary document with ranking and "new hypotheses" and "what we did not find" sections.
- `.system/findings/<timestamp>.json` — a JSON snapshot of all findings following the `shared/schemas/finding.v1.schema.json` schema. Includes `verbatim_check` with a breakdown.

## Finding structure (per `finding.v1`)

- `statement` (one sentence, with an explicit "so what?").
- `elaboration` (1–3 paragraphs of grounding).
- `evidence`: ≥4 respondents, ≥2 verbatim quotes with timecodes.
- `boundaries`: where it does not hold.
- `disconfirms`: contradicting cases.
- `addresses_research_questions`, `addresses_hypotheses`.
- `supporting_themes`, `supporting_categories`, `supporting_paradigm_nodes`, `supporting_types`.
- `confidence` + `confidence_rationale`.
- `implication`: what to do, for whom, expected effect, priority.
- `verbatim_check`: result of the quote check.

## Subagent strategy (optional)

For key-findings, parallelization pays off most on the **verbatim check** — the most common error, and one that can be checked mechanically.

- **Manager** (Opus) — drafts candidate findings, fills in the structure.
- **Workers** (Sonnet/Haiku, one per finding) — verbatim-check each quote against `.system/coded/`, verify ≥4 supporting_respondents, look for additional disconfirms.
- **Manager** integrates, marks `verbatim_check.passed`, and decides the fate of each finding.

The full worker prompts are in `prompts/key-findings.md`, the "Worker prompts" section.

## Production prompt

The full prompt — with verbatim-check rules, templates for `findings.md` and `F0X.md`, and worker prompts — is in `prompts/key-findings.md`.

## DoD

- [ ] 5–7 findings.
- [ ] Each one pinned to ≥4 respondents and ≥2 verbatim quotes.
- [ ] Each one has an explicit implication.
- [ ] Ranking done by strength of evidence.
- [ ] "New hypotheses" section filled in (even if empty — note "none emerged").
- [ ] "What we did NOT find" section filled in.
- [ ] All quotes passed the verbatim check.

## Failure modes

- **Data recap.** "Respondents often talked about X" is not a finding, it is a statement of fact. Ask "so what?" — if there is no answer, reframe it or drop it.
- **Duplicate findings.** Two findings about the same thing — merge them or sharpen the distinct emphasis.
- **Confidence: high everywhere.** Suspicious. Real data yields varying confidence.
- **Too many findings (>9).** That is no longer "key." Trim. Fewer and to the point is better.
- **Fabricated quote.** A critical error. Verify the verbatim before recording.
- **Implication = "we need to improve the UX."** That is not an implication. Be specific — what to change, for whom, with what expected effect.

## Mode behavior

- **assistive**: pause; in chat, a list of 5–7 lines (the statements) plus an offer to read findings/F0X.md. Wait for edits.
- **autonomous**: record it; in `concerns.md` note where confidence is low and why.

## STOP — handoff after this skill

`17-key-findings` closes out the analysis block. The next step is the `18-report-draft` outline (see AGENT.md §14.1). Hard rule §14.0: **do not run 18 without explicit confirmation from the researcher.**

By `session_budget`:

- `low` — handoff is **required**. The full report is written in a new session.
- `normal` — handoff is **required**. Same.
- `high` — handoff is desirable. Analysis context and report assembly are different working modes.

When the trigger fires:

1. Append a **"Handoff to next session"** section to the top of `.system/agent-notes.md`. Inside: which findings are final, which are under review by the researcher, what to read in the new session (at minimum — `findings.md`, `findings/F0X.md`, `model.md`, `typology.md`), and what NOT to read (raw transcripts and `.system/coded/*.json` — they are already aggregated).
2. Print the STOP-handoff block per the AGENT.md §14.2 template, with separators.
3. **Do not run** `18-report-draft`. Wait for an answer.

If the researcher replies "let's continue here" — record it in `agent-notes.md` and continue. **Silence ≠ confirmation.**
