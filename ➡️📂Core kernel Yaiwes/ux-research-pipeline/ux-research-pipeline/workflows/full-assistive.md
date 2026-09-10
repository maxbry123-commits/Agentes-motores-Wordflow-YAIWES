# Workflow: full-assistive

Full research cycle with human pauses. The default.

## Trigger

- `project-config.yaml` has `mode: assistive` (or the field is empty — that's the default).
- Any new activity in the project: the researcher said "let's get started" / dropped a meeting recording in `0-input/` / dropped interviews in `2-interviews/`.

## Preconditions

- `project-config.yaml.name` is filled in (at least a placeholder).
- API keys are present in `.env` (at minimum an LLM key + Mistral Voxtral for STT).

## Sequence

### Phase 1. Preparation (stages 1–4)

1. **Trigger: a meeting recording in `0-input/`** or an explicit "let's get started" request.
   - `06-transcribe` → transcribe the meeting (if there's audio).
   - `01-brief-intake` → draft brief in `1-methodology/brief.md`.
   - In chat: the gist of the task + 2–3 design options.
   - **Pause.** Wait for the researcher's reaction.

2. **After the brief is agreed.**
   - `02-rq-audit` → research questions + hypotheses in `1-methodology/questions-and-hypotheses.md`.
   - In chat: the list of research questions with testability notes.
   - **Pause.**
   - When finalized — ask the researcher to copy them into `project-config.yaml` (the `research_questions` and `hypotheses` fields).

3. **Optional: desk research.**
   - If the researcher asks "what do we know about topic X" — `03-desk-research`.
   - Result — in `1-methodology/desk-research.md`.

4. **Interview guide.**
   - `04-guide-builder` → `1-methodology/guide.md`.
   - In chat: the key blocks + a flag if there are leading questions.
   - **Pause.**

5. **Screener.**
   - `05-screener` → `1-methodology/screener.md` (includes criteria, quotas, instructions for the recruiter).
   - **Pause.**

### Phase 2. Data collection (stages 5–6)

6. **Trigger: each new interview in `2-interviews/`.**
   - `06-transcribe` → transcript `<name>.txt`.
   - `07-quick-summary` → a summary for the team `<name>-summary.md`. **On by default — skip only if the researcher said "don't do summaries."**
   - `09-flat-coding` → coded JSON in `.system/coded/<name>.json`.
   - Optional (only if `enable_screen_vlm: true` in config): `08-screen-vlm` over screenshots.
   - In chat: "coded interview N. Saturation is at such-and-such. Strong quote: '...'."

7. **After each coded interview — update the analysis map** (this is part of the incremental process):
   - Create or update `3-analysis/respondents/<name>.md`.
   - Update `3-analysis/themes/*.md` for themes mentioned in the interview.
   - `11-matrix-pivot` → regenerate `3-analysis/matrix.xlsx`.
   - `10-saturation-map` → update saturation in the matrix ("Saturation" sheet) + `3-analysis/_index.md`.

### Phase 3. Analysis (stages 7–8)

8. **Trigger: number of coded interviews >= `draft_findings_after_n_interviews` (default 5).**
   - `12-link-detector` → links between segments/interviews.
   - `13-axial-coding` → categories in `3-analysis/themes/` (updated with new category attributes).
   - `14-paradigmatic-model` → update `3-analysis/model.canvas`. **Always do this**, even if the researcher doesn't ask — it's your internal structure for the final deliverable.
   - `15-disconfirm-triangulate` → look for disconfirming cases and triangulation.
   - `16-typology` (if the data allows: 8+ interviews with variety) → `3-analysis/types/*.md` + `3-analysis/typology.md`.
   - In chat: "here's what's taking shape — take a look at `3-analysis/_index.md`. Ready to draft the first findings."
   - **Pause.**

9. **After "do the findings."**
   - `17-key-findings` → `3-analysis/findings/*.md` + `3-analysis/findings.md` (consolidated).
   - In chat: 5–7 statements + an explicit confidence-level note.
   - **Pause.**

### Phase 4. Output (stages 9–11)

10. **When the researcher says "let's do the report."**
    - `18-report-draft` → `4-output/report.md`.
    - In chat: "here's the draft. Pay special attention to the recommendations — I marked them `[draft]`. Read it and revise."
    - **Pause for editing.**

11. **"Format it as docs" (optional).**
    - `19-format` → `4-output/report-formatted.md` + publish if a token is available.

12. **"Make a presentation" (optional).**
    - `20-presentation` → `4-output/presentation.pptx`.

### Phase 5. Feedback collection (in the background, always)

Throughout the project:
- Every meaningful divergence between your draft artifact and the final version in `4-output/` → an entry in `feedback.md` with a category.
- Every prompt snapshot at the moment of a pass → into `.system/prompts-versions/`.
- Every skill run → a log in `.system/runs/`.

## Expected artifacts after a full pass

```
my-research/
├── 0-input/<meeting recording>.mp4 + .txt
├── 1-methodology/
│   ├── brief.md
│   ├── questions-and-hypotheses.md
│   ├── guide.md
│   ├── screener.md
│   └── desk-research.md (if any)
├── 2-interviews/R0X.mp4 + .txt + -summary.md (per interview)
├── 3-analysis/
│   ├── _index.md (updated)
│   ├── respondents/R0X.md (per respondent)
│   ├── themes/*.md
│   ├── types/*.md
│   ├── findings/F0X.md
│   ├── findings.md
│   ├── typology.md
│   ├── model.canvas
│   └── matrix.xlsx
├── 4-output/
│   ├── report.md
│   ├── report-formatted.md (optional)
│   └── presentation.pptx (optional)
├── thoughts.md (the researcher writes)
├── feedback.md (filled in along the way)
└── .system/* (logs and snapshots)
```

## Failure modes and what to do

- **The researcher doesn't respond to a pause.** Don't move on by yourself. After 2–3 days you may gently remind them: "on project X — I'm waiting for your reaction to the guide draft." Don't propose alternatives on your own.
- **Transcription failed** (Voxtral returned an error). Log the error in `.system/runs/`, tell the researcher "transcription failed — check the file; the audio may be too quiet or in an unsupported format."
- **Coding fails on the verbatim check.** Don't insert the quote; leave a placeholder with the timecode and a note "verify quote manually."
- **Saturation isn't growing between interviews.** That's normal for the first 3–4. If after 6+ nothing is closing — flag it to the researcher: the guide may be too broad, or the segment is wrong.
- **The researcher says "do the report" at N < 3 interviews.** Say: "the data is thin. Do you want a skeleton draft, or shall we wait for more interviews?" Don't do it silently.
