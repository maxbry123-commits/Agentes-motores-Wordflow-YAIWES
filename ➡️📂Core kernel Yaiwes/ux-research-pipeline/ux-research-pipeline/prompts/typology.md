# typology — production prompt

**Skill:** `16-typology`
**Prompt version:** v0.2 (zero-shot)
**Output schema:** `shared/schemas/typology-type.v1.schema.json`
**Also writes:** `3-analysis/types/<slug>.md` (one map per type), `3-analysis/typology.md` (summary)

The main risk is substituting demographics. The anti-pattern check is built into the prompt and validates a type BEFORE it's written.

---

## Calibration

```yaml
types_count: 2..4                  # types; 4 is the maximum
min_interviews_to_build: 8         # below this, don't build a typology at all
min_representatives_per_type: 2    # a type with 1 representative is a case
behavior_markers_per_type: 3..5
anti_markers_per_type: 1..2
illustrating_quotes_per_type: 1..3
demographic_marker_tolerance: 0    # zero demographic markers allowed in behavior_markers
soft_check_mode: true              # soft mode — flag and record, don't discard
                                    # (see the "Check strictness" section)
```

---

## Check strictness

The default is **soft mode**:

- If even one `anti_pattern_check` item fails, the type is still written, but `anti_pattern_check.passed: false` and `anti_pattern_check.checks.<name>.note` holds the specific issue. The final typology `3-analysis/typology.md` explicitly separates "passed the check" from "draft."
- Strict mode (the type isn't written at all) is not the default right now. It's enabled via `analysis.typology.strict_check: true` (if such a flag appears in config).

This preserves intermediate results for the researcher to review and decide on, rather than handing back a blank page.

---

## System instruction

You are building a behavioral typology of respondents. Types are not quota segments, not demographics. Types are **different strategies and motivations** found in the data and useful for recommendations.

**Hard rules:**

1. **Not demographics.** A type's markers are actions and motivations, not age/gender/city/experience. "Tries to compare everything before choosing" — yes. "Over 35" — no.
2. **Not re-segmentation.** If your types coincide with the screener segments (new/experienced), that's not a typology, you found nothing new.
3. **Not a textbook typology.** "Novices / Experts / Skeptics" is not a finding, it's a template. The names should sound like they're about this product.
4. **At least 2 respondents per type.** 1 respondent = a case, not a type. If a type is "tempting" but has only one representative, flag it and keep it as an observation.
5. **A type must be useful.** Every type requires a `product_implication` — what to DO differently for this type. No implication = the type is useless.
6. **Verbatim quotes with a timecode for every type.** At least 1 quote. The verbatim must match `coded-segment.verbatim` in `.system/coded/`.
7. **Anti-markers are mandatory.** Every type has a "what it definitely is NOT." This helps separate it from neighboring types.

---

## Input

- All `.system/coded/<name>.json` interviews in the project.
- `3-analysis/_categories.md` from `13-axial-coding`.
- `3-analysis/model.md` from `14-paradigmatic-model`.
- `3-analysis/_disconfirms.md` (if present, from `15-disconfirm-triangulate`).
- `project-config.yaml` — `segments` (so you do NOT repeat them in the types).

---

## Algorithm

1. **Check readiness.** If `<8` interviews or all from one segment, do NOT build a typology. Say: "too little data for a typology, need N more interviews" / "all interviews are from one segment, need others." Don't play hero.

2. **Scan the action strategies.** From the paradigm model, take all nodes with the `action_strategy` role. These are your hypotheses about types — who uses which strategy.

3. **Cluster respondents by strategy.** For each respondent, determine the dominant strategy (or combination). Groups of respondents with similar strategies are candidates for a type.

4. **Formulate 2–4 types.** For each:

   - **`name`** — a short phrase about behavior. Metaphors from the respondents' language work well ("optimum hunter," "cautious explorer," "habit as anchor," "through advice").
   - **`summary`** — 2–4 sentences on how the type behaves.
   - **`behavior_markers`** (3–5) — what it does. Verb phrases. "Compares 3+ options before choosing," "starts with search, not the catalog," "turns to colleagues for validation."
   - **`anti_markers`** (1–2) — what it does NOT do. "Doesn't use filters," "doesn't finish reading descriptions," "doesn't use the support chat."
   - **`representative_respondents`** (≥2) — specific respondents.
   - **`illustrating_quotes`** (≥1) — verbatim with a timecode.
   - **`distribution_in_sample`** — "most of the new users," "several experienced users," without percentages.
   - **`product_implication`** — what to do differently. At least 1 sentence, concrete. NOT "improve the UX."
   - **`linked_categories`** / **`linked_paradigm_nodes`** — links to axial and the model.

5. **Anti-pattern check** (apply to all types BEFORE writing):

   - `not_demographic` — go through `behavior_markers`. Are there any "young," "experienced," "city dwellers," "with a lot of experience"? If so, `pass: false`, `note: "{marker}"`.
   - `exclusive_core` — for each pair of types: do they have a set of markers the other lacks? If the core isn't mutually exclusive, `pass: false`.
   - `min_representatives` — `len(representative_respondents) >= 2`.
   - `has_illustrating_quote` — `len(illustrating_quotes) >= 1` AND each `verbatim` exists in `.system/coded/<name>.json` (verbatim check).
   - `useful_downstream` — `product_implication` is non-empty AND concrete (not "improve the UX").

6. **Sanity checks (additional, separate from anti_pattern_check):**

   - **Mutual exclusivity.** Could respondent R03 fit two types at once? If so, reconsider the boundaries. As a last resort, mark the respondent "hybrid" in `notes`.
   - **One type huge, the rest small?** This may be normal, but check: is the definition of the dominant type too broad?
   - **Mapping to segments not 1:1?** Good. If each type = one segment (new = type A, experienced = type B), that's demographics smuggled into a typology. Reconsider.

7. **Record:**

   - `3-analysis/types/<slug>.md`, one map per type.
   - `3-analysis/typology.md` — the summary.
   - JSON in `.system/typology/<timestamp>.json` for downstream.

---

## Output — structure of `3-analysis/typology.md`

```markdown
---
type: typology
last_updated: YYYY-MM-DD
status: draft   # draft / stable
types_count: N
types_passing_check: M   # of N, how many passed anti_pattern_check
respondents_covered: K   # of the total
schema_version: typology-type.v1
---

# Behavioral typology

## TL;DR
{{1–2 lines: which types, what matters most}}

## Summary table

| Type | In brief | Distribution | Passed check | Implication |
|---|---|---|---|---|
| [[types/optimum-hunter]] | compares options, looks for the best | most of the new users | ✅ | redesign of product comparison |
| [[types/habit-as-anchor]] | returns to the familiar | several experienced users | ✅ | save the "last choice" |
| [[types/through-advice]] | asks colleagues/family | a single case, see note | ⚠️ only 1 representative | content for "share" |

## Types

### [[types/optimum-hunter]] — TY01

(short summary of the type map; the full one is in the file)

### [[types/habit-as-anchor]] — TY02

...

## Types that didn't pass the check

(if any — here they are, with an explanation of what failed)

### TY03 — "through-advice" ⚠️
- **Failed:** `min_representatives` — only R05 clearly fits, R11 is borderline.
- **What to do:** listen for it in upcoming interviews, or reformulate as an edge case.

## Sanity checks

- Mutual exclusivity: ✅ / ⚠️ ({{R0X fits both TY01 and TY02 equally — marked hybrid}}).
- Dominant type: TY01 covers ~half the sample — normal.
- Mapping to segments not 1:1: ✅ (TY01 appears in both new and experienced).

## Links to the model and categories

| Type | Categories | Paradigm nodes |
|---|---|---|
| TY01 | C01, C03 | N02 (causal), N05 (action) |
| TY02 | C04 | N06 (action), N09 (consequence) |

## Open questions

- {{where a type's boundaries are unclear}}
- {{which new markers to look for in upcoming interviews}}
```

---

## Output — structure of `3-analysis/types/<slug>.md`

```markdown
---
type: typology_type
type_id: TY0X
name: {{name}}
slug: {{slug}}
representative_respondents: [R03, R07]
distribution: "most of the new users"
anti_pattern_check_passed: true   # or false with a note below
schema_version: typology-type.v1
---

# {{type name}}

## TL;DR
{{2–3 sentences on how the type behaves}}

## Behavioral markers

- {{marker 1 — a verb phrase}}
- {{marker 2}}
- {{marker 3}}
- {{marker 4}}

## Anti-markers (what it does NOT do)

- {{anti-marker 1}}
- {{anti-marker 2}}

## Representatives

- [[R03]]: {{short descriptor, why this type}}
- [[R07]]: ...

## Illustrating quotes

> "..." — [[R03]] `[mm:ss]`
> "..." — [[R07]] `[mm:ss]`

## Distribution in the sample

{{most of the new users; several experienced users}}

## Product implication

{{What to DO differently for this type. Concretely — what to change, for whom, with what expected effect.}}

## Links

- Categories: [[3-analysis/_categories#C01]], [[#C03]].
- Model nodes: [[3-analysis/model#N02]] (causal), [[#N05]] (action).

## Anti-pattern check

{{if passed=true — a short line "passed all checks";
if false — a list with notes}}
```

---

## Worker prompts

If `use_subagents: true` and you ended up with 3+ types, it makes sense to do **per-type validation** in parallel. Workers receive: one candidate type, all `coded-interview.v1.json`, the current categories and model. The worker's task:

1. Verbatim check for `illustrating_quotes`, each quote against `.system/coded/`.
2. For each `representative_respondent`, find 2–3 segments in their interview supporting the `behavior_markers`. If fewer, flag it.
3. Apply `anti_pattern_check` to this type: go through all 5 items, return `{check_name: {pass, note}}`.
4. Additionally: go through ALL respondents (not just representative_respondents) — find 1–2 who also exhibit this type's markers. If any, a candidate for expansion.

The worker returns: `{type_id, verbatim_check: {passed, failed: [...]}, anti_pattern_check: {...}, additional_candidates: [...]}`. The manager integrates.

---

## DoD

- [ ] 2–4 types (if there's enough data; otherwise an empty typology with an explanation).
- [ ] Each type has ≥2 representatives, ≥1 verbatim quote, ≥3 behavior_markers, ≥1 anti_marker.
- [ ] anti_pattern_check done for each type, result in `anti_pattern_check.passed`.
- [ ] `product_implication` is non-empty and concrete.
- [ ] Mutual exclusivity checked.
- [ ] Verbatim quotes passed the check.
- [ ] Maps in `3-analysis/types/` created, the summary `typology.md` assembled.

---

## Failure modes

- **Types = quota segments.** You found nothing, the typology is redundant. Don't record it as a finding.
- **One type huge, the rest tiny.** Sometimes normal, but usually a broad definition. Narrow the main type.
- **A respondent fits three types.** The types are poorly separated. Redo.
- **product_implication = "improve the UX."** That's not an implication. Reformulate concretely or remove the type.
- **A type on 1 respondent.** That's a case. Note it separately in `typology.md`, not as a full type.
- **Demographic labels in behavior_markers.** The most common error. Rewrite the markers through actions and motivations.

---

## Mode behavior

- **assistive**: pause, and in chat give the types and distribution, explicitly noting "these passed anti_pattern_check, these are drafts." Wait for the researcher's reaction — the typology goes into the final deliverable.
- **autonomous**: record, and in `concerns.md` note the types that didn't pass the check, with specifics on what exactly failed.
