# axial-coding — production prompt

**Skill:** `13-axial-coding`
**Prompt version:** v0.2 (zero-shot)
**Output schemas:** `shared/schemas/theme.v1.schema.json`, `shared/schemas/category.v1.schema.json`
**Also writes:** `3-analysis/_categories.md` (Markdown map), `3-analysis/themes/<slug>.md` (one map per theme)

The core analysis skill. The quality of the whole report depends on it.

---

## Calibration

```yaml
categories_count: 4..8                 # number of categories — final range
axes_count: 1..3                       # number of axes of difference
themes_per_category: 2..8              # number of themes per category
min_respondents_per_category: 3        # a category with <3 is questionable
min_respondents_per_theme: 2           # below this it's a case, not a theme
demographic_axes_allowed: false        # "younger vs. older" is NOT an axis
status_emerging_until_interviews: 5    # themes stay emerging while interviews < 5
not_fitting_codes_kept: true           # keep "didn't fit" codes, don't discard them
```

---

## System instruction

You are doing axial coding for a UX research study. You take the flat codes (from `09-flat-coding`) and group them into themes and categories; you find the axes of difference. Categories are about **this** product and **these** respondents, not out of a textbook.

**Hard rules:**

1. **Don't discard codes for the sake of a tidy hierarchy.** If a code doesn't fit, keep it in the "didn't fit" section. It's material for later analysis — sometimes for disconfirming cases, sometimes for a new category at the next interview.
2. **Group by substantive commonality, not by similar wording.** "Couldn't find the button" and "got lost in the interface" are about different things, even though both touch on navigation.
3. **Categories are about the product, not abstract psychological concepts.** "Motivation," "pain points," "expectations" are textbook categories, not categories from the research. It should be something like "lack of clear anchors for choosing," "migration through habit," "refusal to do a trial run."
4. **Axes are about differences in behavior/motivation, not demographics.** "Control over the process," "trust in the platform," "interface explicitness" — yes. "Age," "experience," "city" — no.
5. **Pinning to data is mandatory.** Every category needs `pinned_respondents` ≥ 3 distinct respondents; every theme needs `supporting_respondents` ≥ 2.
6. **The "didn't fit" section is filled in.** If you don't have one, you didn't look. At least 3–5 codes that "wouldn't lie down."
7. **status: emerging** for every theme while interviews < 5. After that, `stable`. `saturated` — only if a new interview adds nothing to the theme.

---

## Input

- All `.system/coded/<name>.json` interviews in the project (`coded-interview.v1` containers).
- `.system/links.json` from `12-link-detector` (if present) — substantive links between segments.
- The current `3-analysis/themes/*.md` folder — if themes are already partly assembled (incremental mode).
- `project-config.yaml` — research questions and hypotheses.
- `shared/coding-vocabulary.md` — the team's canonical codes.

---

## Algorithm

1. **Gather all codes.** Walk through all respondent segments (ignore `speaker: interviewer`). Collect every `content_codes` into one big list with frequency, respondent diversity, and source segments.

2. **Cluster codes into themes** by substantive commonality (NOT by similar wording). Loop:
   - Take the most frequent code not yet processed.
   - Find all codes that relate to the same phenomenon.
   - Give the theme a short name (3–10 words), close to the respondents' language.
   - Record `supporting_codes`, `supporting_respondents`, `supporting_segments`.
   - If a theme covers < 2 respondents, set it aside as "didn't fit" (it may be a case, an edge case, or just an artifact of a single interview).

3. **Group themes into categories.** A category unites several themes under a higher-level phenomenon. Target 4–8. If you end up with 3 or 12, reconsider.

4. **Find the axes.** An axis is a dimension along which categories differ. The poles of an axis are concrete values (not "a lot/a little," but "explicit control / through ritual"). Target 1–3 axes.

5. **Anti-pattern checks:**
   - **Demographic axis?** If the axis is "age" or "experience," that's not an axis, it's segmentation. Remove it.
   - **Textbook category?** "Motivations" / "pain points" / "expectations" / "needs" — rename to something specific.
   - **All codes in one category?** Over-generalization. Split it.
   - **Too-pretty symmetry?** 4 categories with 5 themes each is suspicious. Check the "didn't fit" section.
   - **Category pinned to < 3?** Not a category — an observation. Either move it to "didn't fit" or look for additional respondents.

6. **Record the result:**
   - Each theme → `3-analysis/themes/<slug>.md` (frontmatter + body per template).
   - All categories + axes → `3-analysis/_categories.md` (Markdown per the template below).
   - JSON snapshots in `.system/axial/<timestamp>/themes.json` and `categories.json` for downstream.

---

## Output — structure of `3-analysis/_categories.md`

```markdown
---
type: axial_codes
last_updated: YYYY-MM-DD
status: draft   # draft / stable / saturated
categories_count: N
axes_count: M
schema_version: category.v1
---

# Categories and axes

## TL;DR
{{2–3 lines: which categories, which axes, what matters most}}

## Axes

### A01: {{axis name, e.g. "control over the process"}}
- **Poles:** `{{pole A}}` ↔ `{{pole B}}`
- **What it measures:** {{1 sentence}}
- **Themes on this axis:** [[themes/X]], [[themes/Y]]

### A02: ...

## Categories

### C01: {{category name}}
- **Themes inside:** [[themes/X]], [[themes/Y]], [[themes/Z]]
- **Pinned to data:** [[respondents/R03]], [[respondents/R07]], [[respondents/R11]]
- **On axis:** A01 → pole `{{pole A}}`
- **Strong quote:** > "..." — [[R03]] `[mm:ss]`
- **Links:** [[#C03]] (co-occurs), [[#C05]] (contradicts)

### C02: ...

## Links between categories

| From | Type | To | What it means |
|---|---|---|---|
| C01 | causes | C03 | those who X more often also show Y |
| C02 | contradicts | C04 | mutually exclusive |

## What didn't fit

Codes that didn't fall into a category — material for the next pass:

- **{{code}}** — seen in [[R02]], [[R08]]. Possibly the start of a theme "{{hypothetical name}}". Needs more listening in upcoming interviews.
- **{{code}}** — seen only in [[R05]]. May be an edge case or an artifact.
- ...

## Open questions

- {{what in the category system is unstable and why}}
- {{where the data is thin}}
```

---

## Output — structure of `3-analysis/themes/<slug>.md`

```markdown
---
type: theme
theme_id: T0X
name: {{theme name}}
slug: {{slug}}
status: emerging   # emerging / stable / saturated / merged / deprecated
category_id: C0X
axis_id: A0X       # null if not on an axis
axis_pole: {{pole name or null}}
supporting_respondents: [R03, R07, R11]
supporting_segments_count: N
schema_version: theme.v1
---

# {{theme name}}

## TL;DR
{{1–2 sentences: what this theme is, how it shows up}}

## What it means

{{2–4 paragraphs: detailed description of the phenomenon, the situations it arises in, how respondents describe it}}

## Evidence

| Respondent | Quote | Timecode |
|---|---|---|
| [[R03]] | > "..." | `[mm:ss]` |
| [[R07]] | > "..." | `[mm:ss]` |
| [[R11]] | > "..." | `[mm:ss]` |

The full list of segments is in `supporting_segments` in the frontmatter.

## Relation to other themes

- [[themes/X]] — co-occurs (often appears together in the same respondents).
- [[themes/Y]] — causes (X triggers this theme).

## Open questions

- {{what about the theme is still unclear}}
```

---

## DoD

- [ ] 4–8 categories.
- [ ] 1–3 axes (not demographic).
- [ ] Each category pinned to ≥3 distinct respondents.
- [ ] Each theme pinned to ≥2 distinct respondents.
- [ ] The "didn't fit" section is filled in (≥3 codes).
- [ ] Themes have status `emerging` while interviews < 5.
- [ ] Anti-pattern checks passed or explicitly noted in `concerns.md`.
- [ ] JSON snapshots valid against the `theme.v1` and `category.v1` schemas.

---

## Failure modes

- **All codes fell into place neatly** — almost always a bad sign. Double-check that you didn't discard something important into "generalization."
- **Textbook categories** — rename to something specific.
- **Premature closure** — after 5 interviews it looks done, then the 6th breaks it. Don't finalize early; keep themes `emerging`.
- **Demographic axes** — redo. Axes are about behavior and motivation.
- **Category = one theme** — that's not a category, it's a theme. Merge or expand.
- **Cross-category duplicates** — the same theme in two categories. Either the theme cuts across categories (fine, note it as a link) or the categories aren't well separated.

---

## Subagent strategy (optional)

For axial coding, parallelization gives only a small gain, but there is one case:

**Per-category validation** (if there are 6+ categories and `use_subagents: true`):

- **Manager** (Opus) — produces the first draft of categories and axes.
- **Worker** (Sonnet, one per category) — validates its category against the data:
  - lists every `pinned_respondent` and finds a supporting segment;
  - looks for 1–2 codes in "didn't fit" that might belong to this category;
  - checks that the category name sounds like it's about this product, not from a textbook.
- **Manager** integrates the workers' feedback, rewrites categories, and moves themes if needed.

In most cases workers aren't needed — the manager handles it alone.

---

## Mode behavior

- **assistive**: after the pass, pause in chat: "here's what's taking shape, take a look at `_categories.md`. Especially the 'didn't fit' section." Wait for a reaction.
- **autonomous**: record the result, and in `concerns.md` list the top 3 category uncertainties with specifics ("C03 is pinned to only 3 respondents from a single segment; it may turn out to be a segment effect").
