---
name: saturation-map
description: Computes theme coverage across interviews — how many respondents have closed each theme, which themes are emerging/forming/saturated. Trigger — after each newly coded interview. Updates the "Saturation" sheet in `3-analysis/matrix.xlsx` and the progress table in `3-analysis/_index.md`. In an interactive session — optionally creates a live artifact with a dashboard.
stage: 5.4
status: stretch
---

# 10-saturation-map

## Why

After each new interview it helps to see:
- Which themes are firmly closed (recur stably across different respondents).
- Which themes are only starting to surface (are more interviews needed).
- Which themes were expected but never appeared (the interview guide may need adjusting).

This drives the decision to "stop now or recruit 3 more people."

## Trigger

After `09-flat-coding` for each interview.

Can also be invoked on its own by request: "show saturation" / "how well have we closed it."

## Inputs

- All `.system/coded/*.json` for the project.
- `3-analysis/themes/*.md` (to know which themes exist).
- `project-config.yaml.segments` (for quotas).

## Outputs

1. **The "Saturation" sheet in `3-analysis/matrix.xlsx`**:
   | Theme | Respondents covering | % of sample | Status | Last updated |

2. **The "Saturation" section in `3-analysis/_index.md`** — a table plus one paragraph of commentary.

3. **(Optional, in an interactive session)** a live artifact — an HTML dashboard with a dynamic chart of coverage by theme and segment.

## Computation logic

- **emerging**: 1–2 respondents mentioned the theme.
- **forming**: 3–5 respondents; the contours of the theme are visible but not closed.
- **saturated**: 6+ respondents **with diversity** (not all from one segment); the theme is closed.

"Diversity" is taken into account: if all mentions of a theme come from a single segment, the status **stays forming**, and a flag appears in `_index.md`: "theme X is closed only on segment Y."

## Prompt skeleton (commentary in `_index.md`)

```
Based on the coded interviews, update the "Saturation" section in `_index.md`:

What you have:
- A list of themes with their statuses.
- A list of segments and quotas.
- Coverage by theme × segment.

Do this:
1. A table: theme / N respondents / % of sample / status / segment diversity.
2. A one-paragraph comment: what's closed, what's only starting to surface, what never appeared.
3. If there are candidates for stopping recruitment — flag them explicitly: "themes X, Y, Z are closed; we can stop after 1–2 more interviews if no new themes appear."
4. If there are gaps — flag them: "themes A, B were expected but never appeared; the interview guide may not be drawing them out."

Don't invent a status. The difference between forming and saturated is count and diversity.
```

## DoD

- [ ] The "Saturation" sheet in `matrix.xlsx` is updated.
- [ ] The section in `_index.md` is updated.
- [ ] Themes with status "expected but never appeared" are flagged explicitly.

## Failure modes

- **Themes from a single segment marked as saturated.** Don't mark them — that's a segment effect, not a general property.
- **Too many themes (>30) — all emerging.** You're probably not grouping synonymous codes. At this stage just show them as is; the later `13-axial-coding` will merge similar ones.
- **Saturation grows linearly across interviews.** That's suspicious (the curve usually plateaus after 6–8). If it's linear, the interview guide may be touching different themes each time (bad).

## Mode behavior

- **assistive**: after each update, a short chat message: "Saturation: theme X is closed, theme Y is starting to surface. After the next interview I'll be ready to draft findings."
- **autonomous**: update the files and move on, no chat messages.
