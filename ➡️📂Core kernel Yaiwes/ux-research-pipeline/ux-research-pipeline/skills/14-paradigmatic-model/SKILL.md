---
name: paradigmatic-model
description: Builds the grounded-theory paradigm model — conditions → context → actions → consequences — from the axial categories. Trigger — after `13-axial-coding`. The main tool for structuring analysis on the team. **It is always built** for every study (even if the researcher doesn't show it in the final report), because it is the foundation of the coding. Delivered as an updatable Obsidian canvas plus a textual summary.
stage: 8.8
status: core
---

# 14-paradigmatic-model

## Why

The grounded-theory paradigm model is the primary analysis frame on the team. All coding rests on it.

Structure:
- **Conditions** (causal conditions): what triggers the phenomenon, under what preconditions.
- **Context**: the circumstances in which it arises.
- **Actions**: what the respondent does in this situation (strategies).
- **Consequences**: what happens next, the outcome.

This is **not** one of many optional lenses. It is the **primary tool** — like a mind map for an architect.

## Trigger

After `13-axial-coding`. Invoked ALWAYS — even if the researcher didn't request it.

Recompute after each new interview or any substantial change to the categories.

## Inputs

- `3-analysis/_categories.md` (from `13-axial-coding`).
- All `.system/coded/*.json` (for evidence quotes).
- `3-analysis/themes/*.md` (to enrich the model's nodes).

## Outputs

- `3-analysis/model.canvas` — an Obsidian canvas with nodes and arrows (Obsidian-format JSON).
- `3-analysis/model.md` — textual companion to the canvas. Structure per the template in `prompts/paradigmatic-model.md`.
- `.system/paradigm/<timestamp>/nodes.json` — JSON of nodes per the `shared/schemas/paradigmatic-node.v1.schema.json` schema.
- `.system/paradigm/<timestamp>/arcs.json` — JSON of arrows (we use `$defs.arc` from the same schema).

Canvas color coding (rules in `prompts/paradigmatic-model.md`): 1=causal_condition (red), 2=context (orange), 3=action_strategy (yellow), 4=consequence (green), 5=intervening_condition (light blue), 6=hypothetical (purple).

## Production prompt

The full prompt with the rules for filling the four blocks, the `model.md` and `model.canvas` templates, and anti-pattern checks lives in `prompts/paradigmatic-model.md`.

## DoD

- [ ] All 4 blocks are filled in.
- [ ] Every node has a pin to a quote.
- [ ] At least 3 main arrows.
- [ ] Gaps and hypothetical nodes are flagged explicitly.
- [ ] Canvas and md are in sync.

## Failure modes

- **An "everything connects to everything" model** is not a model, it's a network. A real model has clear arrows and explicit gaps.
- **A node without a quote pin** is interpretation without evidence. Don't leave it.
- **Too beautiful, too symmetric.** Real data is contradictory. If the model comes together easily, double-check that you haven't smoothed something over.
- **A duplicate of the axial coding.** The model should be a **different** level of abstraction. If the model's nodes = the axial categories, something is wrong. The model's nodes are **process** labels (causal conditions, actions), not taxonomic categories.

## Mode behavior

- **assistive**: after generation, a short message: "the model is ready, open `model.canvas` in Obsidian." No pause — this is an intermediate artifact.
- **autonomous**: write it, and in `concerns.md` record the low-confidence hypothetical nodes.

## Use downstream

The model is used in:
- `15-disconfirm-triangulate` — searching for disconfirming cases = searching for data that breaks the model's arrows.
- `17-key-findings` — each key finding can reference nodes or arrows of the model.
- `18-report-draft` — the model is optionally included in the report (either the diagram or a textual description of the dynamics).
