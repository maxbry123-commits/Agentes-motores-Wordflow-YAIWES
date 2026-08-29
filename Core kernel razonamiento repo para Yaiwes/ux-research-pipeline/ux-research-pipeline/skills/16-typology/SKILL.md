---
name: typology
description: Builds a behavioral (NOT demographic) typology of respondents. Trigger — 8+ coded interviews with variety. The main risk is substituting demographics ("young vs older"). The skill runs a built-in anti-pattern check and **does not produce a typology** if it fails the check. Includes behavioral markers, anti-markers, and illustrative quotes.
stage: 8.7
status: stretch
---

# 16-typology

## Why

A typology is a powerful tool for the report and for recommendations: different actions for different types of users.

But it is the **riskiest** analysis skill. The main mistakes:
- Substituting the typology with demographics ("the young," "city dwellers," "the experienced").
- Types that are not mutually exclusive.
- Types that are never used downstream in the conclusions (a typology "for the shelf").

## Trigger

After 8+ coded interviews with variety across segments.

If there are fewer than 8 interviews, or they are all from one segment — **do not run the typology**. Say instead: "not enough data for a typology, we need N more interviews."

## Inputs

- All `.system/coded/*.json`.
- `3-analysis/_categories.md` (from axial).
- `3-analysis/model.md` (from paradigmatic).
- `3-analysis/_disconfirms.md` (from disconfirm).

## Outputs

- `3-analysis/types/<slug>.md` — one Markdown card per type. Template in `prompts/typology.md`.
- `3-analysis/typology.md` — a summary document with a table and a separate list of types that "failed the check" (see the "Strictness of the check" section in the prompt).
- `.system/typology/<timestamp>.json` — a JSON snapshot of all types following the `shared/schemas/typology-type.v1.schema.json` schema. Includes `anti_pattern_check` with a breakdown for each check.

## Anti-pattern check (built-in)

5 checks are applied BEFORE writing each type:

1. **Not demographics.** Markers are actions and motivations, not age/gender/city/experience.
2. **Mutually exclusive core.** Each type has a set of markers that other types lack.
3. **Illustrative quotes.** ≥1 verbatim quote with a timecode (the verbatim exists in `.system/coded/`).
4. **At least 2 representatives.** 1 representative = a case, not a type.
5. **Useful downstream.** A non-empty `product_implication`.

The result of each check goes into `anti_pattern_check.checks.<name>` with the structure `{pass: bool, note: string}`. **The mode is soft** (see the prompt): the type is recorded even if a check fails, but `anti_pattern_check.passed: false` and it is separated out in `typology.md`. The full wording of the checks and the algorithm are in `prompts/typology.md`.

## Subagent strategy (optional)

When `analysis.agent_coding.use_subagents: true` and there are 3+ types — **per-type validation** in parallel:

- **Manager** (Opus) — drafts the candidate types.
- **Workers** (Sonnet/Haiku, one per type) — verbatim-check the quotes, verify behavior_markers for each representative_respondent, apply the 5 anti-pattern checks, and look for additional candidate representatives.
- **Manager** integrates the workers' results, rewrites the types, or flags them.

The full worker prompts are in `prompts/typology.md`, the "Worker prompts" section.

## Production prompt

The full prompt — with rules for the anti-pattern check, templates for `typology.md` and `types/<slug>.md`, and worker prompts — is in `prompts/typology.md`.

## DoD

- [ ] 2–4 types.
- [ ] Each one passed the anti-pattern check.
- [ ] Each one has ≥2 representatives.
- [ ] Each one has a verbatim quote.
- [ ] `typology.md` links to `_categories.md` and `model.md`.
- [ ] The summary distribution table is filled in.

## Failure modes

- **The types are just quota segments.** "New vs experienced" is not a typology — it was already known from the screener. A typology should reveal a **new** division.
- **One type is huge, the rest are tiny.** This may be normal (one type dominates), but check that the definition isn't too broad.
- **Types overlap behaviorally.** If respondent R03 fits three types equally well, the typology does not work — redo it.
- **Types with no impact.** If you cannot say what to **do differently** for each type in a product recommendation, the typology is useless — leave it out of the final.

## Mode behavior

- **assistive**: pause, show the types and the distribution in chat, wait for the researcher's reaction. The typology goes into the final, so human judgment is critical here.
- **autonomous**: record it; in `concerns.md` note which types are borderline and where you are unsure.
