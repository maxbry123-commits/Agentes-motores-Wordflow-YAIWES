# Workflow: audit-external

Re-checking the work of an external agency.

## Trigger

- The researcher said something like "the agency delivered it, re-check their work" / "I need an audit by next week."
- `0-input/` contains the agency's materials: their transcripts, their report.
- `project-config.yaml` has `mode: autonomous`.

## Preconditions

- Transcripts from the agency (in any format — `.docx`, `.pdf`, `.txt`).
- Their final report (`.pdf` / `.docx` / `.md`).
- Optionally — their interview guide and screener.

## What the agent does

### Step 1. Normalize the input

1. Convert the agency's transcripts into our format (JSON with timecodes if present; without timecodes if they have none — note this in `concerns.md`).
2. Put the normalized transcripts in `2-interviews/<name>.txt` and in `.system/coded/<name>-source.json`.
3. If they have a guide and a screener — put them in `1-methodology/source-guide.md`, `1-methodology/source-screener.md`.
4. Their report — in `0-input/source-report.<ext>`.

### Step 2. Independent analysis

Run through the standard analysis pipeline:
- `09-flat-coding` on each transcript.
- `11-matrix-pivot`, `10-saturation-map`.
- `12-link-detector`, `13-axial-coding`.
- `14-paradigmatic-model`.
- `15-disconfirm-triangulate`.
- `16-typology` (if applicable).
- `17-key-findings`.

Done the same way as in `full-autonomous.md`, but without `01-brief-intake`, `02-rq-audit`, `04-guide-builder`, `05-screener` (the agency already did those).

### Step 3. Compare against their report

This is the part unique to this workflow.

1. Extract the key findings and recommendations from their report (`0-input/source-report.<ext>`).
2. Cross-check against your own key findings.
3. Fill in `4-output/audit.md`:

```markdown
# Audit — {{agency name}}

## Overall impression

{{1–2 paragraphs: how solid the work is, what's strong, what's weak}}

## Confirmed

| Their finding | Your assessment | Evidence |
|---|---|---|
| ... | confirmed / partial / diverges | link to your finding or quote |

## They reinterpreted

| Their claim | What the data actually shows | Where the gap is |
|---|---|---|
| ... | ... | ... |

## They missed

| What was missed | Where it shows in the data | Why it matters |
|---|---|---|
| ... | ... | ... |

## Quote check

| Quote in their report | Found verbatim? | If not — what the transcript actually says |
|---|---|---|
| "..." | yes / no / similar but different | ... |

## Recommendations before using their report

- {{what to use as-is}}
- {{what to use with caveats}}
- {{what NOT to use}}
```

### Step 4. Handoff

The standard `4-output/handoff.md` (as in `full-autonomous.md`), plus an extra `## Audit` section linking to `4-output/audit.md`.

## Failure modes

- **Their transcripts have no timecodes.** Verbatim quote-checking gets easier (just `grep`), but if a quote was heavily edited, it won't be found. Note this in `concerns.md`.
- **Their report is a PDF with complex formatting.** Use the `pdf` skill to extract the text, then parse the findings manually (via the LLM). Remember: not all PDFs parse equally well — verify the key passages.
- **Their findings rest on numbers** ("72% said…"). If they only have 12 interviews, that's a methodological error on their part. Flag it explicitly in `audit.md` and **do not reproduce** the percentages in your own wording.
- **Their recommendations read like finished product decisions.** This is often a sign of substitution: a recommendation ≠ a finding. Note which recommendations actually follow from the data and which are guesses.

## What the agent does NOT do

- Does not publish the audit externally. That is always the researcher's final step.
- Does not write in a snide or fawning tone — a neutral methodological register. The audit is a working tool, not a weapon.
