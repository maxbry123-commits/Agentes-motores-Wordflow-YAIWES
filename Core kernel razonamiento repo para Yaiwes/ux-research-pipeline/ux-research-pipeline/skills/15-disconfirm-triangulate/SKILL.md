---
name: disconfirm-triangulate
description: Active search for disconfirming cases and triangulation. Merges 8.5+8.6. Trigger — after `13-axial-coding` and `14-paradigmatic-model`. Deliberately hunts for data that violates the emerging model: marginal voices, negative cases, divergences between sources. The key point — do NOT stop at the first confirmation.
stage: 8.5+8.6
status: stretch
---

# 15-disconfirm-triangulate

## Why

The most common error in qualitative analysis is confirmation bias. An analyst finds a pattern and starts seeing support for it everywhere, ignoring contradictions.

This skill explicitly looks for **what does NOT fit**. It belongs in the DoD of every study; without this step the analysis is weak.

## Trigger

After `13-axial-coding` and `14-paradigmatic-model`.

Can also be invoked on its own: the researcher says "find what argues against it."

## Inputs

- `3-analysis/_categories.md` (from axial).
- `3-analysis/model.md` + `3-analysis/model.canvas` (from paradigmatic-model).
- All `.system/coded/*.json`.
- `1-methodology/desk-research.md` (if it exists) — for triangulation against external sources.
- `project-config.yaml.hypotheses` — what we set out to test in the first place.

## Outputs

- `3-analysis/_disconfirms.md` — list of disconfirming cases found.
- `3-analysis/_triangulation.md` — where sources converge, where they diverge.

### `_disconfirms.md`

```markdown
---
type: disconfirms
last_updated: TODO
disconfirm_count: 0
status: draft
---

# Disconfirming cases

> Deliberate search for what violates the emerging model.

## By model node

### Node "{{node name}}"

- **Disconfirm 1**: [[respondents/R0X]] does the opposite.
  - Quote: > "..." [mm:ss]
  - Is this a fluke or a subgroup? Check the segments.

### Node "..."

## By axial categories

### Category "{{name}}"

- **Edge case**: code {{X}} did not fit into any category, but it shows up in [[R0X]] and [[R0Y]] — a new category may be needed.

## By hypotheses

### H1: "{{hypothesis}}"

- **Contradicts**: [[R0X]] — quote.
- **Supports**: [[R0Y]] — quote.
- **Mixed**: [[R0Z]] — quote.

## By respondent types

### Type "{{X}}"

- **Does not match the type**: [[R0X]] partly fits, but carries a strong marker of another type.

## What we did NOT find (though we looked)

- {{expected contradiction that is absent}}: possibly a sampling effect, or the hypothesis genuinely held up.
```

### `_triangulation.md`

```markdown
---
type: triangulation
last_updated: TODO
sources_compared: ["interviews", "desk_research"]
---

# Triangulation

## By theme

### Theme "{{X}}"

| Source | What it says | Confidence |
|---|---|---|
| Interviews | {{short summary}} | high |
| Desk research | {{takeaway from external sources}} | medium |
| Internal expertise | {{note from the researcher's thoughts or prior studies}} | low |

**Converges?** yes / partly / diverges. If it diverges — possible reasons why.

### Theme "..."
```

## Prompt skeleton

```
You are running an active search for disconfirming cases in a UX study. The goal is NOT to confirm the model, but to find what violates it.

Given:
- Paradigm model: {{insert `model.md`}}.
- Categories: {{insert}}.
- Hypotheses: {{insert from project-config}}.
- All codes: {{material}}.

Task:
1. For every model node — find at least one disconfirming case, or explicitly say "none found."
2. For every category — find edge cases.
3. For every hypothesis — split respondents into supporting / contradicting / mixed.
4. Add a section "what we did NOT find (though we looked)" — that is also a result.

Hard rules:
- A disconfirming case must be **substantive**, not "said one word against it once." A behavior, a quote, an explicit disagreement.
- Flag it: is the disconfirm a fluke, or a subgroup (a stable pattern within a sub-segment)?
- If you find too many disconfirms (>5 per node) — the model is probably wrong. Flag for an axial revision.
- "No disconfirms found" is **suspicious**, not "good." Real data is contradictory.

Triangulation:
1. For each theme, compare: what the interviews say, what desk research says (if any), what the team's accumulated knowledge says (from the thoughts notes).
2. Where it converges, where it diverges.
3. If it diverges — possible reasons why (different segments, stale data, different methods).
```

## DoD

- [ ] Every model node has had a disconfirm search (even if nothing was found).
- [ ] Hypotheses checked: supporting / contradicting / mixed.
- [ ] "What we did not find" section filled in.
- [ ] Triangulation done for every theme (if desk research exists).

## Failure modes

- **"No disconfirms" across the whole pipeline** — almost always a bad sign. Double-check that you are not substituting a "refinement" for a disconfirm.
- **Disconfirm without grounding** ("R03 talked about something else") — not a disconfirm. You need a quote plus a substantive contradiction.
- **Triangulation with no divergences** — also suspicious. External and internal data usually diverge at least on nuance.
- **Blindly following desk research** when it conflicts. If the interviews say X and desk research says Y — that is an interesting case, not "we need to redo the interviews."

## Mode behavior

- **assistive**: after the pass — a short summary in chat: "found N disconfirms, the main one is [[R0X]] contradicting node Y. Triangulation: divergence on theme Z." No pause (this is a working step, not a finale).
- **autonomous**: write and move on. Put the top-3 disconfirms that need the researcher's attention in `concerns.md`.
