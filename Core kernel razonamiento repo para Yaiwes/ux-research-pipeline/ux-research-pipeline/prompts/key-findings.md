# key-findings — production prompt

**Skill:** `17-key-findings`
**Prompt version:** v0.2 (zero-shot)
**Output schema:** `shared/schemas/finding.v1.schema.json`
**Also writes:** `3-analysis/findings/F0X.md` (one file per finding), `3-analysis/findings.md` (summary)

The most visible artifact of the study. The main pitfalls are data recap, missing implications, and fabricated quotes.

---

## Calibration

```yaml
findings_count: 5..7              # key findings; more than that — switch to stage 18, not findings
min_respondents_per_finding: 4    # below this it's a case, not a finding
min_quotes_per_finding: 2         # verbatim
percent_words_forbidden: true     # no "60% said"
data_recap_forbidden: true        # "respondents often talked about X" — NOT a finding
verbatim_check_required: true     # every quote exists in `.system/coded/`
new_hypotheses_section: required  # a separate list of what wasn't in the brief
not_found_section: required       # hypotheses that did NOT hold up
```

---

## System instruction

You assemble the 5–7 key findings of the study. This is the conclusion of the analysis. A finding is not a recap of the data, but a conclusion with a product implication.

**Hard rules:**

1. **Conclusions, not data recap.** "Respondents often mentioned onboarding" is a data recap. "New users use search as a crutch for navigation because the menu is unclear to them" is a finding.
2. **Every finding answers one or more research questions.** If it answers none, it goes into the "new hypotheses" section, not the main findings.
3. **At least 4 respondents per finding.** Fewer is a case or an edge case, not a finding.
4. **At least 2 verbatim quotes with a timecode.** Every quote MUST match `coded-segment.verbatim` in `.system/coded/<name>.json`. Don't fabricate, splice, or edit.
5. **No percentages** on qualitative data. "Most," "several," "one," "a single observation."
6. **Every finding has a concrete implication.** NOT "improve the UX." Concretely: what to do, for whom, expected effect.
7. **Confidence: high everywhere — suspicious.** Real data yields varying confidence. If all findings are high, double-check.
8. **The "new hypotheses" section is mandatory.** These are patterns that weren't in the original brief. Each one is a testable formulation.
9. **The "what we didn't find" section is mandatory.** Hypotheses from `project-config.yaml.hypotheses` that did NOT hold up are also a result.
10. **A finding should be useful to a product manager or designer, not just an analyst.** If a product-manager reader doesn't understand what to do next, reformulate.

---

## Input

- `3-analysis/_categories.md` from `13-axial-coding`.
- `3-analysis/model.md` + nodes and arcs from `14-paradigmatic-model`.
- `3-analysis/_disconfirms.md` from `15-disconfirm-triangulate` (if run).
- `3-analysis/_triangulation.md` (if run).
- `3-analysis/typology.md` from `16-typology` (if built).
- All `.system/coded/<name>.json` (for the verbatim check).
- `project-config.yaml` — research questions and hypotheses.
- `thoughts.md` — the researcher's notes (read them! they often hold an insight that isn't in the data).

---

## Algorithm

1. **Go through each research question.** For each, find the categories and model nodes that address it. State an answer to the RQ in one paragraph.

2. **Generate finding candidates.** Sources:
   - large categories pinned to ≥4 respondents → candidate;
   - model arcs with `confidence: high` and a `claim` that answers an RQ → candidate;
   - types from the typology with a `product_implication` → candidate;
   - disconfirming cases for major hypotheses → candidate (a negative finding, but a strong one);
   - patterns from `thoughts.md` that you can back up with data.

3. **Select 5–7.** Criteria:
   - covers every RQ with at least one finding;
   - rank by evidentiary strength (number of respondents × segment diversity × presence of disconfirming cases);
   - if one category produces 2 close findings, merge them or sharpen the contrast.

4. **For each finding, fill in:**

   - **`statement`** — one line with an explicit "so what?". Format: "{{what was found}} → {{why it matters for the product}}." For example: "New users skip the catalog because they don't believe they'll find what they need there → defaulting focus to search is justified, but the catalog needs to surface earlier."
   - **`elaboration`** — 1–3 paragraphs of reasoning. Connected prose, not lists.
   - **`addresses_research_questions`** — the specific research questions.
   - **`addresses_hypotheses`** — which hypotheses from the brief the finding confirms/refutes/refines.
   - **`is_new_hypothesis: false`** — for main findings; `true` — for items in the "new hypotheses" section.
   - **`supporting_themes`**, **`supporting_categories`**, **`supporting_paradigm_nodes`**, **`supporting_types`**.
   - **`evidence.respondents`** — a list of ≥4 respondents.
   - **`evidence.quotes`** — ≥2 verbatim quotes. Check each one against `.system/coded/`.
   - **`boundaries`** — where it doesn't hold, in which segment the opposite is true, for whom it's different.
   - **`disconfirms`** — a list of contradicting segments with a note.
   - **`confidence`** — `high` if ≥6 respondents from different segments AND there are disconfirming cases that were checked and refined the boundaries; `medium` if ≥4 respondents from one or two segments; `low` if 4 respondents and no disconfirming cases (not looked for, or not found).
   - **`confidence_rationale`** — 1–2 sentences.
   - **`implication`** — `statement` (what to do), `addressee` (for whom), `expected_effect` (what changes), `priority`.

5. **Verbatim check.** For each quote, search for an exact match in the `.system/coded/<name>.json` segments. If none is found, do NOT record the quote in quotation marks — replace it with a paraphrase without quotes, or delete it. Record `verbatim_check.passed: false` and the list in `failed_quotes`.

6. **The "new hypotheses" section** (`is_new_hypothesis: true`). Patterns that weren't in `project-config.yaml.hypotheses`. Format: a testable formulation + 1–2 quotes + a recommendation for further verification (quantitative? new interviews?).

7. **The "what we didn't find" section.** Go through `project-config.yaml.hypotheses`. For each, which segments confirm/refute it. If a hypothesis did NOT hold up, give it its own item.

8. **Record:**
   - Each finding → `3-analysis/findings/F0X.md` per the `_template-finding.md` template.
   - The summary `3-analysis/findings.md` with the list, ranking, and the "new hypotheses" + "what we didn't find" sections.
   - JSON snapshots in `.system/findings/<timestamp>.json`.

---

## Output — structure of `3-analysis/findings.md`

```markdown
---
type: findings_summary
last_updated: YYYY-MM-DD
status: draft   # draft / stable
findings_count: N
new_hypotheses_count: M
not_found_count: K
schema_version: finding.v1
---

# Key findings

## TL;DR
{{2–3 lines: the gist in a 30-second read}}

## Answers to the research questions

| RQ | In brief | Main findings |
|---|---|---|
| RQ1: ... | {{1–2 sentences}} | [[#F01]], [[#F03]] |
| RQ2: ... | ... | [[#F02]] |

## Findings (ranked by strength)

### F01 — {{statement}}
**Confidence:** high. **Implication for:** CRM product manager.

{{elaboration in 1 paragraph}}

→ see [[findings/F01]] for details.

### F02 — ...

## New hypotheses (not in the brief)

### NH1 — {{formulation}}
Testable: {{how to verify}}.
Support: [[R03]] [mm:ss], [[R07]] [mm:ss].

### NH2 — ...

## What we did NOT find (though we looked)

### H1 (from the brief): "{{hypothesis formulation}}"
**Status:** not confirmed.
**What we found instead:** {{1–2 sentences on what in the data doesn't fit H1}}.

### H2: ...

## Methodological caveats

- Sample: {{N interviews with {{segments}}}}.
- Best covered: RQ1, RQ3. RQ2 — partially, needs more data.
- Disconfirming cases were actively sought. Triangulation: {{yes/no/partial}}.

## Relation to other artifacts

- [[3-analysis/_categories]]
- [[3-analysis/model]]
- [[3-analysis/typology]]
```

---

## Output — structure of `3-analysis/findings/F0X.md`

```markdown
---
type: finding
finding_id: F0X
rank: N
statement: {{one line}}
addresses_research_questions: [RQ1, RQ3]
is_new_hypothesis: false
confidence: medium
respondents_count: 5
quotes_count: 3
verbatim_check_passed: true
schema_version: finding.v1
---

# F0X — {{statement}}

## What was found

{{elaboration: 1–3 paragraphs of reasoning}}

## Evidence

**Respondents:** [[R03]], [[R07]], [[R09]], [[R11]], [[R14]] (5 of 12).

**Quotes:**

> "{{verbatim}}" — [[R03]] `[mm:ss]` (segment seg-0042)

> "{{verbatim}}" — [[R07]] `[mm:ss]` (segment seg-0073)

> "{{verbatim}}" — [[R11]] `[mm:ss]` (segment seg-0091)

**Supporting categories:** [[3-analysis/_categories#C01]], [[#C03]].
**Supporting model nodes:** [[3-analysis/model#N02]] (causal), [[#N05]] (action).
**Related types:** [[3-analysis/types/optimum-hunter]].

## Boundaries of applicability

{{where it doesn't hold; e.g. — for experienced users the pattern is reversed}}

## Counter-evidence and nuances

- [[R08]] [mm:ss] — opposite case. Reason: {{...}}.
- [[R10]] — partially, with the caveat {{...}}.

## Confidence: medium

{{Why medium: 5 respondents from two segments, 1 disconfirming case. For high we'd need ≥6 respondents and active triangulation, which wasn't done here.}}

## Implication

- **What we do:** {{a concrete action in the product}}.
- **Addressed to:** {{team / role}}.
- **Expected effect:** {{what changes in behavior or a metric}}.
- **Priority:** medium.

## Relation to RQs and hypotheses

- **RQ1** ({{question}}): answered directly — {{answer}}.
- **RQ3** ({{question}}): partially answered.
- **H1** (from the brief): confirms.
```

---

## Worker prompts

For key-findings, parallelization gives the biggest gain on the **verbatim check** (it's the most common error and it's checked mechanically). If `use_subagents: true`:

- **Manager** (Opus) — formulates finding candidates, fills in the structure.
- **Workers** (Sonnet/Haiku, one per finding) — verbatim check + optional strength check:

  For each finding the worker receives:
  - the finding object with `evidence.quotes`;
  - all `.system/coded/<name>.json`.

  Worker tasks:
  1. For each quote in `evidence.quotes`, find an exact match in `coded-segment.verbatim` of the corresponding segment. If none is found, mark it in `failed_quotes`.
  2. For each `respondent_id` in `evidence.respondents`, find ≥1 segment in that interview supporting the `statement`. If fewer than 4 respondents actually support it, flag it.
  3. Search for counter-evidence: go through segments coded as contradicting — are there disconfirming cases for this finding? Add them to `disconfirms`.

  The worker returns: `{finding_id, verbatim_check: {passed, failed_quotes: [...]}, supporting_respondents_verified: [...], additional_disconfirms: [...]}`. The manager integrates and decides which finding to keep.

---

## DoD

- [ ] 5–7 findings (if there's enough data; otherwise as many as you got, justified in the TL;DR).
- [ ] Each addresses ≥1 RQ.
- [ ] Each pinned to ≥4 respondents and ≥2 quotes.
- [ ] Verbatim check passed for all quotes (`verbatim_check.passed: true`).
- [ ] Each has a concrete `implication.statement` (not "improve the UX").
- [ ] The "new hypotheses" section is filled in (even if empty — note it explicitly).
- [ ] The "what we didn't find" section is filled in.
- [ ] Confidence varies (not high everywhere).
- [ ] Ranking done by evidentiary strength.

---

## Failure modes

- **Data recap instead of conclusions** — "respondents often said." Reformulate with an explicit "so what?".
- **Duplicate findings** — two about the same thing. Merge or sharpen the contrast.
- **Confidence: high everywhere** — suspicious. Real data yields varying confidence.
- **Too many findings (>9)** — these aren't "key" anymore. Cut them. Fewer and to the point is better.
- **A quote didn't match verbatim** — a critical error. Do NOT put it in quotation marks. Replace with a paraphrase or delete.
- **Implication: "we need to improve the UX"** — that's not an implication. Concretely what to change.
- **All findings address RQ1, nothing on RQ3** — flag it: "RQ3 is weakly covered, more interviews needed."
- **The word "identified" in a statement** — an empty word. Concretely: "new users were observed to…," "while working with filters R03 and R07 couldn't find…".

---

## Mode behavior

- **assistive**: pause, and in chat give a list of 5–7 lines with each finding's `statement` + links to files. Wait for the researcher's edits. Findings go into the final deliverable — the human's judgment is critical here.
- **autonomous**: record, and in `concerns.md` note where confidence is low and why, which quotes failed the verbatim check and were replaced with a paraphrase.
