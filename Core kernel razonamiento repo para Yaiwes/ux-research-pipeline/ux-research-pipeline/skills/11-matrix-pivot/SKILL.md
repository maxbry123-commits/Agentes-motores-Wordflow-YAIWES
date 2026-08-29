---
name: matrix-pivot
description: Regenerates the `respondent × theme` matrix in `3-analysis/matrix.xlsx`. A pure Python script with no LLM; reads all `.system/coded/*.json`, aggregates by theme, fills the "Matrix" sheet with density highlighting (heatmap). Trigger — after each newly coded interview.
stage: 8.1
status: core
---

# 11-matrix-pivot

## Why

The respondent × theme matrix is the simplest and most useful big-picture view of a project. It shows:
- Who said a lot and who said little.
- Which themes are mentioned by everyone and which by only a few.
- Segment patterns (if themes differ across segments).

This is **not an LLM task** — it's simple aggregation done with plain code.

## Trigger

After `09-flat-coding` for each interview.

## Inputs

- All `.system/coded/<name>.json` for the project.
- `3-analysis/themes/*.md` — for canonical theme names (if themes are already named).
- `project-config.yaml.segments` — for segment highlighting in rows.

## Outputs

- The "Matrix" sheet in `3-analysis/matrix.xlsx`.

### Sheet format

| Respondent | Segment | Date | Dur. (min) | Theme 1 | Theme 2 | ... |
|---|---|---|---|---|---|---|
| R01 | new | 2026-MM-DD | 58 | 5 | 0 | ... |
| R02 | experienced | 2026-MM-DD | 64 | 2 | 7 | ... |

Where the number in a cell is the count of mentions of the theme.

**Heatmap coloring** of cells:
- 0 → light gray.
- 1–2 → light purple.
- 3–5 → medium purple.
- 6+ → saturated purple (`#7642E8` at full opacity).

## Implementation

Pure Python via `openpyxl`. Pseudocode:

```python
import json
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

coded_dir = Path('.system/coded')
xlsx_path = Path('3-analysis/matrix.xlsx')

# 1. Load all JSON, build the matrix
respondents = {}
all_themes = set()
for p in coded_dir.glob('*.json'):
    if p.name.endswith('-raw.json') or p.name.endswith('-screen.json'):
        continue
    with open(p) as f:
        data = json.load(f)
    rid = data['respondent_id']
    respondents[rid] = {
        'segment': data.get('segment'),
        'date': data.get('date'),
        'duration_min': data.get('duration_min'),
        'theme_counts': {}
    }
    for seg in data['segments']:
        for code in seg.get('content_codes', []):
            theme = code['theme'] if isinstance(code, dict) else code
            respondents[rid]['theme_counts'][theme] = respondents[rid]['theme_counts'].get(theme, 0) + 1
            all_themes.add(theme)

# 2. Write to xlsx
wb = load_workbook(xlsx_path)
ws = wb['Matrix']
# clear data rows except header
ws.delete_rows(2, ws.max_row)
# write header
ws.cell(row=1, column=1).value = 'Respondent'
ws.cell(row=1, column=2).value = 'Segment'
ws.cell(row=1, column=3).value = 'Date'
ws.cell(row=1, column=4).value = 'Dur. (min)'
themes_sorted = sorted(all_themes)
for i, th in enumerate(themes_sorted):
    ws.cell(row=1, column=5+i).value = th
# write data
for r, (rid, info) in enumerate(sorted(respondents.items()), start=2):
    ws.cell(row=r, column=1).value = rid
    ws.cell(row=r, column=2).value = info['segment']
    ws.cell(row=r, column=3).value = info['date']
    ws.cell(row=r, column=4).value = info['duration_min']
    for i, th in enumerate(themes_sorted):
        cnt = info['theme_counts'].get(th, 0)
        cell = ws.cell(row=r, column=5+i)
        cell.value = cnt
        cell.fill = heatmap_fill(cnt)

wb.save(xlsx_path)
```

Full implementation — `scripts/matrix_pivot.py` (created as implementation progresses).

## DoD

- [ ] The "Matrix" sheet is updated.
- [ ] Heatmap coloring is applied.
- [ ] Respondents are sorted by ID.
- [ ] Themes are sorted by total (the most frequent theme leftmost in the column header).

## Failure modes

- **Themes written with different words across interviews** ("onboarding", "getting started", "first acquaintance"). At this stage **don't merge** — that's the job of `13-axial-coding`. Show them as is; the researcher will see the menagerie and ask to unify.
- **Too many themes (>40)** — the sheet bloats. That's normal at early stages; after `13-axial-coding` themes get grouped.

## Mode behavior

Doesn't matter. This is a purely algorithmic operation and requires no pauses.
