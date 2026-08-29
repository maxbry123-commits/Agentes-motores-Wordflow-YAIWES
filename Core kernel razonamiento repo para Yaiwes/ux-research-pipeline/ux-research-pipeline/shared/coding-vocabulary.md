# Coding vocabulary

The team's canonical codebook. Used as a reference in `09-flat-coding` (for in-vivo codes) and in `13-axial-coding` (to unify synonyms).

**This file lives forever** and is updated as projects accumulate. If you notice a new, stable code that recurs across several studies, add it here.

## How to use it

During flat coding (`09-flat-coding`):
- If a respondent says something close to one of the canonical phrasings, use the canonical one.
- If a respondent says something **new** that does not appear in this list, keep the in-vivo code — do not force it into an existing one.

During axial coding (`13-axial-coding`):
- This vocabulary is a **hint**, not a rule. The real categories are determined by the data of the specific project.

## Canonical codes

> A starter set. Grow it as projects accumulate. Each code is a short phrase plus 1–2 examples of respondent speech.

### Group: onboarding and first impression

- `first-entry-difficult` — the respondent describes trouble in the first steps. Examples: "I didn't get where to tap," "I searched for about five minutes."
- `onboarding-ignored` — skipped the tutorial / tips. "Closed it right away," "I never read those things."

### Group: search and navigation

- `search-as-navigation` — the respondent uses search instead of the menu. "I just search, I don't dig into the catalog."
- `result-unclear` — the respondent is unsure about the result. "I didn't understand what it gave me."
- `clarification-needed` — an extra step is required. "First I googled it, then came here."

### Group: recommendations and personalization

- `recommendation-useful` — the respondent uses recommendations.
- `recommendation-intrusive` — the respondent gets annoyed.

### Group: control and agency

- `wants-more-control` — the respondent wants settings. "I'd like to choose for myself."
- `trusts-the-system` — the respondent relies on the algorithm. "Let it decide on its own."

### Group: errors and recovery

- `error-without-explanation` — something doesn't work and the respondent doesn't understand why.
- `recovery-difficult` — many actions are needed to fix it.

### Group: social and emotional

- `trusts-the-platform` — statements about trust.
- `distrusts-the-platform` — statements about suspicion, especially around privacy.
- `emotional-attachment` — the respondent describes positive emotions toward the product.

## Content categories (orthogonal to codes)

A conceptual taxonomy of what a segment is *about*, used as an analytic lens — not a machine-facing field. Do not confuse it with the content codes above. Note: the machine-facing `content_type` enum (`fact` / `interpretation` / `hypothesis`) is defined in `shared/schemas/coded-segment.v1.schema.json`; this list is a separate conceptual layer.

| category | Meaning |
|---|---|
| `insight` | A new observation or realization by the respondent. |
| `problem` | The respondent describes a problem. |
| `wish` | The respondent wants to add or change something. |
| `action` | The respondent describes something they do. |
| `state` | The respondent describes their state or situation. |
| `process` | The respondent describes a sequence of steps. |

## Anti-patterns in coding

- **Code too general** (`user-did-something`). Useless — it doesn't distinguish anything.
- **Code too specific** (`tapped-the-green-button-in-the-corner`). Doesn't generalize. Use abstraction.
- **Emotion-as-code** with no content (`annoyed`). Emotion falls under the `state` content category; the content code should describe **what** the reaction is about.
- **Grouping at the coding stage.** "I'll put every mention of search under `search`." NO — at the flat-coding stage, preserve variety. Grouping happens in `13-axial-coding`.

## Update rules

When adding a new code to this file:
1. Check that there isn't a close existing one.
2. Add it to the right group, or create a new one (but be careful — more than 8 groups and the taxonomy falls apart).
3. Give an example of respondent speech and the context in which the code was used.
4. In the commit message: `vocab: added code "X" from project Y`.
