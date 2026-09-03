---
name: pptx
description: Presentation creation, editing, and analysis. When Claude needs to work with presentations (.pptx files) for creating new presentations, modifying content, working with layouts, adding speaker notes, or any presentation tasks.
source: anthropics/skills
license: Apache-2.0
---

# PowerPoint Processing

## Creating Presentations (Python)

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Add title slide
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Hello, World!"
subtitle.text = "python-pptx demo"

# Add content slide
bullet_slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(bullet_slide_layout)
shapes = slide.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Key Points"
tf = body_shape.text_frame
tf.text = "First bullet point"
p = tf.add_paragraph()
p.text = "Second bullet point"
p.level = 1

prs.save('presentation.pptx')
```

## Adding Images

```python
from pptx.util import Inches

blank_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_layout)

left = Inches(1)
top = Inches(1)
width = Inches(5)
slide.shapes.add_picture('image.png', left, top, width=width)
```

## Adding Tables

```python
rows, cols = 3, 4
left = Inches(1)
top = Inches(2)
width = Inches(6)
height = Inches(1.5)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(2)

# Add content
table.cell(0, 0).text = "Header 1"
table.cell(1, 0).text = "Data 1"
```

## Adding Charts

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['East', 'West', 'Midwest']
chart_data.add_series('Sales', (19.2, 21.4, 16.7))

x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
)
```

## Editing Existing Presentations

```python
prs = Presentation('existing.pptx')

# Access slides
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text_frame.text)

# Modify text
slide = prs.slides[0]
slide.shapes.title.text = "New Title"

prs.save('modified.pptx')
```

## Best Practices

- Use slide layouts for consistency
- Keep text minimal, use visuals
- Use Inches() or Pt() for sizing
- Save frequently during creation

## Design & Aesthetics (Practical Rules)

Use these guidelines when generating or editing slides so the deck looks intentional, modern, and consistent.

### Layout & Grid

- Prefer a **simple grid** (e.g., 12-column feel) and align everything to consistent left edges.
- Keep a **single dominant focal point** per slide (one headline + one visual or one chart).
- Use generous **margins/whitespace**. As a rule of thumb, keep key content inside ~10% padding from slide edges.
- Keep **consistent spacing** between elements (e.g., 8/16/24/32 px style steps). Avoid “almost equal” gaps.

### Typography & Hierarchy

- Use **1 font family** (or 2 at most: one for headings, one for body). Avoid mixing many fonts.
- Establish clear hierarchy:
  - Title: ~36–44 pt
  - Section header: ~28–34 pt
  - Body: ~18–24 pt
  - Caption/footnote: ~12–14 pt
- Keep line length comfortable; avoid long paragraphs. Prefer **bullets with strong nouns/verbs**.
- Use bold for emphasis, avoid underlines; italics only sparingly.

### Color System

- Use a restrained palette:
  - 1 primary accent color
  - 1 neutral dark (text)
  - 1 neutral light (background)
  - Optional 1 secondary accent
- Maintain contrast: dark text on light background (or vice versa). Avoid low-contrast gray-on-gray.
- Use color to encode meaning consistently (e.g., success=green, risk=red) and keep it consistent across slides.

### Visuals (Icons / Images / Shapes)

- Prefer **high-quality visuals** with consistent style (all flat icons, or all line icons—not mixed).
- Avoid stretching images; preserve aspect ratio and crop intentionally.
- Use subtle shape styling: thin strokes, soft shadows (if any), consistent corner radius.
- Avoid decorative clutter: every icon/shape should clarify structure or meaning.

### Images / Illustration Direction

- Prefer **one visual style per deck**: photo-real, 3D renders, flat illustration, or line illustration. Don’t mix styles.
- **Resolution**: use sufficiently large images (avoid blurry screenshots). If an image will be full-width, it should be at least ~1920px wide.
- **Cropping**: crop for composition (rule of thirds, clear subject). Avoid awkward cut-offs (hands/heads) unless intentional.
- **Backgrounds**: prefer clean backgrounds; remove busy backgrounds when they distract. If needed, place images on a solid/blurred panel.
- **Color & tone**: keep color temperature and contrast consistent across slides; apply the same tint/duotone treatment if used.
- **Text on images**: ensure readability with overlay scrims/gradient, and keep contrast high. Avoid putting text over noisy areas.
- **Icon usage**: keep icon stroke weight and corner style consistent; avoid mixing filled and outline icons in the same row.
- **Captions & sources**: if the deck is external-facing, add a small caption/source line for non-original images.
- **Licensing**: use properly licensed assets; avoid random web images for public decks unless attribution/license is clear.

### Charts & Tables

- Remove chart junk: minimize gridlines, borders, and unnecessary labels.
- Use **one highlight color** to direct attention; keep other series neutral.
- Prefer direct labels over legends when possible.
- Keep tables minimal: light row separators, consistent number formats, right-align numbers.

### Consistency Checklist (Quick)

- Same title position across slides
- Same font sizes for same roles (title/body/caption)
- Same color usage for same semantics
- Same alignment rules (left edges, baseline alignment)
- No overlapping elements; equal spacing; no “almost aligned” objects