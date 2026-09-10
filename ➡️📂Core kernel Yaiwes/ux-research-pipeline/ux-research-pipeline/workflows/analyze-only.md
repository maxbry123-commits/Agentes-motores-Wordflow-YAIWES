# Workflow: analyze-only

Only stages 7–9 on existing transcripts.

## Trigger

- `2-interviews/` already contains transcripts (`.txt`) or their audio (the agent transcribes first).
- `1-methodology/questions-and-hypotheses.md` (or `project-config.yaml.research_questions`) contains research questions — otherwise coding would have no structure to work against.
- The researcher said "code what we have and give me findings" / "I need a draft report from the existing interviews."

## When applicable

- An older study that was never coded — you need to go back and analyze it.
- Your own interviews plus interviews from an agency — on a single pipeline.
- Part of a full cycle where the researcher wrote the brief and the interview guide themselves but wants the analysis automated.

## Preconditions

- Transcripts in `2-interviews/<name>.txt` or audio (the agent transcribes).
- A list of research questions and hypotheses — present in the project.
- (Optional) the interview guide (`1-methodology/guide.md`) — helps during the global coding pass.

## What the agent does

### Step 1. Transcription (if needed)

For every audio file without a transcript — `06-transcribe`.

### Step 2. Coding

For every transcript — `09-flat-coding`. Coded JSON → `.system/coded/<name>.json`.

### Step 3. Respondent profiles

For every coded transcript — a profile in `3-analysis/respondents/<name>.md`.

### Step 4. Themes and matrix

- `11-matrix-pivot` → `3-analysis/matrix.xlsx`.
- Create/update `3-analysis/themes/*.md`.
- `10-saturation-map` → "Saturation" sheet in the matrix + `3-analysis/_index.md`.

### Step 5. Analysis

- `12-link-detector`.
- `13-axial-coding` → updating themes as categories.
- `14-paradigmatic-model` → `3-analysis/model.canvas`.
- `15-disconfirm-triangulate`.
- `16-typology` (if the data allows).
- `17-key-findings` → `3-analysis/findings/*.md` + `3-analysis/findings.md`.

### Step 6. Final

- If the researcher said "report" — `18-report-draft` → `4-output/report.md`.
- If they said "docs" — `19-format`.
- If they said "presentation" — `20-presentation`.

## assistive vs autonomous within analyze-only

If `project-config.yaml` has `mode: assistive` — pause after all interviews are coded, after the first axial draft, after the key findings.

If `mode: autonomous` — no pauses; at the end produce `4-output/handoff.md` + `concerns.md` (as in `full-autonomous.md`).

## Failure modes

- **No research questions.** Coding is still possible (you'll get a generic labeling), but mapping to research questions is impossible. Tell the researcher: "there are no research questions — I can code without the mapping, but findings without research questions are structurally weaker. Do you want to define research questions retroactively?"
- **Transcripts without timecodes.** Verbatim quotes can be verified, but you can't cite a timecode. Note this in `concerns.md`. In the report use the format `"quote" — R0X` without `[mm:ss]`.
- **Transcripts of very uneven quality.** Some with good diarization, some as one block of text. Mark each interview in `3-analysis/respondents/R0X.md` (frontmatter: `transcript_quality: good | medium | poor`). Account for this in axial coding and findings: poor-quality interviews may yield less reliable codes.
- **The agency's guide doesn't match your view of the topic.** Don't try to "rename" their blocks. Preserve their structure during coding; reframe it during axial coding.
