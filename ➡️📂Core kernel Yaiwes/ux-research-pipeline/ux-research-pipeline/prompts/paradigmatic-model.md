# paradigmatic-model — production prompt

**Skill:** `14-paradigmatic-model`
**Prompt version:** v0.2 (zero-shot)
**Output schema:** `shared/schemas/paradigmatic-node.v1.schema.json` (model nodes and arcs)
**Also writes:** `3-analysis/model.canvas` (Obsidian canvas), `3-analysis/model.md` (text)

A core methodological instrument. It is built **always**, even if the researcher doesn't show it in the final report.

---

## Calibration

```yaml
nodes_count: 6..12                  # usually 2–4 per paradigm role
arcs_count_main: 3..8               # main arcs
roles_required:
  - causal_condition
  - context
  - action_strategy
  - consequence
roles_optional:
  - intervening_condition           # add only if there's data
min_respondents_per_node: 1         # a node without at least one pin is not allowed
hypothetical_threshold_respondents: 2   # nodes pinned to < 2 → is_hypothetical: true
contradictions_kept: true           # keep contradictions in the model, don't smooth them over
process_label_required: true        # a node name = a process label
```

---

## System instruction

You are building a grounded-theory paradigm model: **causal_condition → context → (intervening_condition) → action_strategy → consequence**. This is not a visualization of categories — it's a **different level of abstraction**: processes and their links, not a taxonomy.

**Hard rules:**

1. **The model is about a specific phenomenon, not "about the product in general."** The top line of `model.md` is the TL;DR: which dynamic the model describes. If you can't say it in one phrase, the model hasn't come together — don't write it.
2. **Every node is pinned to at least one quote with a timecode.** A node without a pin is an interpretation without evidence. Not allowed.
3. **A node name is a process label**, not a taxonomy. "Lack of clear anchors for choosing" — yes. "Anchors for choosing" — no (that's a category, not a process).
4. **Hypothetical nodes — explicitly.** If a node is supported by 1–2 respondents and is methodologically needed for the model's coherence — `is_hypothetical: true`, `confidence: low`, and marked with an asterisk in `model.md`.
5. **Keep contradictions.** If respondents diverge on a node, two arcs with different `consequence`s are better than one smoothed-over arc.
6. **Don't duplicate axial.** Model nodes should NOT match categories. If you have `causal_condition: "Lack of anchors for choosing"` and a category `C03: "Lack of clear anchors for choosing,"` reformulate the node as a process ("Searching for anchors → not finding them → switching to habit").
7. **Arcs are claims.** An arc is the statement "under condition X in context Y, action Z occurs with consequence W," not just a line.

---

## Input

- `3-analysis/_categories.md` from `13-axial-coding`.
- All themes `3-analysis/themes/*.md`.
- All `.system/coded/<name>.json` (for quote pins).
- `.system/links.json` from `12-link-detector` (if present).
- `project-config.yaml` — research questions.

---

## Algorithm

1. **Read the categories and the links between them.** Pay special attention to `causes`, `modulates`, `contradicts` links.

2. **State the central phenomenon.** In one phrase: which dynamic unfolds in this study. For example: "Respondents search for clear anchors for choosing → don't find them → switch to habit or advice → consequences for retention." If you can't, don't build the model; ask the researcher.

3. **Fill in the four blocks:**

   - **causal_condition (N01..N0X)** — what triggers the phenomenon, the preconditions. Usually 2–4 nodes.
   - **context** — the circumstances in which the phenomenon arises. Segment, temporal context, emotional backdrop. 1–3 nodes.
   - **intervening_condition** (optional) — what amplifies or blocks the move to action. E.g. a past negative experience, the presence of a hint. 0–3 nodes.
   - **action_strategy** — what the respondent does in this situation. Usually 2–4 nodes, one per typical strategy.
   - **consequence** — what happens next. 2–4 nodes.

4. **For each node:**
   - `name` — a process label.
   - `description` — 1–3 sentences on what the node means.
   - `linked_themes` — which axial-coding themes "feed" it.
   - `supporting_segments` — pin to data. At least 1 segment.
   - `confidence` — `high` if ≥4 respondents and different segments, `medium` if 2–3, `low` if 1.
   - `is_hypothetical` — `true` if the pin < `hypothetical_threshold_respondents`.
   - `canvas_position.color` — by role (1=red causal, 2=orange context, 3=yellow action, 4=green consequence, 5=blue intervening, 6=purple hypothetical).

5. **Draw the main arcs (3–8).** An arc is a claim:
   - `kind`: `causes` / `modulates` / `blocks` / `co-occurs`.
   - `claim` — the statement text.
   - `supporting_segments` — pin to the segments supporting this link (not just nodes — the link itself!).
   - `confidence`.

6. **Find the gaps.** Where data is thin, where the model is "hypothetical," where there are contradictions. Record this in the "Gaps" section of `model.md` and in `concerns.md`.

7. **Write `model.canvas`** — JSON in the Obsidian canvas format (see below) with nodes and arcs.

8. **Write `model.md`** — the text companion per the template below.

---

## Output — structure of `3-analysis/model.md`

```markdown
---
type: paradigmatic_model
last_updated: YYYY-MM-DD
status: draft   # draft / stable
nodes_count: N
arcs_count: M
schema_version: paradigmatic-node.v1
---

# Paradigm model

## TL;DR
{{1–2 sentences: the key dynamic the model describes}}

## Central phenomenon

{{1 paragraph: what unfolds in the data, which dynamic}}

## Conditions (causal_conditions)

### N01: {{node name}}
- **What it means:** {{1–2 sentences}}
- **Themes:** [[themes/X]], [[themes/Y]]
- **Pin:** [[R03]] [mm:ss], [[R07]] [mm:ss]
- **Confidence:** medium
- **Quote:** > "..." — [[R03]] `[mm:ss]`

### N02: ...

## Context

### N0X: ...

## Intervening conditions (if any)

### N0X*: {{name}} ⚠️ hypothetical — R05 only

## Actions (action_strategies)

### N0X: ...

## Consequences (consequences)

### N0X: ...

## Main arcs

### E01: N01 → N0X (causes)
**Claim:** under condition {{X}} in context {{Y}}, action {{Z}} occurs with consequence {{W}}.
**Pin:** [[R03]] [mm:ss] — "..."; [[R07]] [mm:ss] — "...".
**Confidence:** high.

### E02: N02 → N0X (modulates)
**Claim:** ...
**Pin:** ...
**Confidence:** medium.

| From → To | Type | In brief | Confidence |
|---|---|---|---|
| N01 → N0X | causes | ... | high |
| N02 → N0X | modulates | ... | medium |

## Hypothetical nodes and arcs

(everything with `is_hypothetical: true` or `confidence: low`)

- **N0X* — {{name}}**: supported only by [[R05]] and [[R11]]. Needs interviews to confirm.
- **E0X — N01 → N0X (causes)**: the link is visible only in respondents from the "new" segment. May turn out to be a segment effect.

## Gaps in the model

- {{where there's no data; e.g. we don't see the transition from X to Y in experienced users}}.
- {{contradictions: where respondents diverge and we kept both branches}}.
- {{what needs quantitative verification — e.g. the frequency of action_strategy in the population}}.

## Relation to other artifacts

- [[3-analysis/_categories]] — the categories that feed the nodes.
- [[3-analysis/_disconfirms]] — where the model breaks, see `15-disconfirm-triangulate`.
- [[3-analysis/typology]] — which respondent types use which strategies.
- [[3-analysis/findings]] — which findings rely on the model's nodes/arcs.
```

---

## Output — `3-analysis/model.canvas`

An Obsidian canvas is JSON with nodes and arcs:

```json
{
  "nodes": [
    {
      "id": "N01",
      "type": "text",
      "text": "**N01: Lack of anchors for choosing**\n\n[[themes/anchors-for-choosing]]\n\n> \"...\" — R03",
      "x": 0,
      "y": 0,
      "width": 280,
      "height": 140,
      "color": "1"
    }
  ],
  "edges": [
    {
      "id": "E01",
      "fromNode": "N01",
      "fromSide": "right",
      "toNode": "N05",
      "toSide": "left",
      "label": "causes"
    }
  ]
}
```

Lay it out horizontally, left to right: causal → context → intervening → action → consequence. Nodes of the same role go in a column.

---

## DoD

- [ ] All 4 required roles filled in (causal_condition, context, action_strategy, consequence).
- [ ] At least 6 nodes total, usually 8–12.
- [ ] Each node pinned to ≥1 quote with a timecode.
- [ ] At least 3 main arcs, each with a `claim` and a pin.
- [ ] Hypothetical nodes and arcs marked explicitly.
- [ ] The TL;DR fits in 1–2 sentences.
- [ ] The "Gaps" section is filled in.
- [ ] Canvas and md are in sync (nodes and arcs match).
- [ ] The JSON of nodes and arcs is valid against `paradigmatic-node.v1` (including `$defs.arc`).

---

## Failure modes

- **"Everything is connected to everything"** — that's a network, not a model. Reduce the number of arcs to the main ones.
- **Nodes are copies of axial categories** — reformulate them as process labels. A node = a process, a category = a taxonomy.
- **Too symmetrical, too pretty** — real data is contradictory. If the model came together easily, check that you didn't smooth over the contradictions.
- **A node with no quote pin** — interpretation without evidence. Don't leave it.
- **Can't write the TL;DR** — the model hasn't come together; ask the researcher or wait for more interviews.
- **Too many hypothetical nodes (>30%)** — the model is premature. Mark `status: draft` and note it in `concerns.md`.

---

## Mode behavior

- **assistive**: after generation, a short message: "the model is ready, open `model.canvas` in Obsidian. Pay special attention to the hypothetical nodes and the gaps." Don't pause — this is an intermediate artifact.
- **autonomous**: record, and in `concerns.md` note the hypothetical nodes and arcs, their rationale, and what's needed to raise confidence.

---

## Downstream use

- `15-disconfirm-triangulate` — actively searching for data that violates the model's arcs.
- `17-key-findings` — each key finding may reference nodes/arcs.
- `18-report-draft` — the model is optionally included in the report (either the canvas as an image or text).
