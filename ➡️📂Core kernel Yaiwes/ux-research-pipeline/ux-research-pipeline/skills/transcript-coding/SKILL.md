---
name: transcript-coding
description: "Flat coding of in-depth interview transcripts. Turns a raw JSON transcript (array of utterances with timecodes) into a structured JSON of coded segments ready for analysis: verbatim quotes, subject codes, content types, mapping to research questions, interpretive notes. Stage 7 in the UX research pipeline — runs after transcription (ux-transcribe) and before analysis. Default backend: OpenAI GPT-5.4; Claude Opus 4.7 and Gemini also supported via config.yaml. Works on one file or a whole project folder, maintains a running project-wide codebook. Trigger on any of: 'code this transcript', 'run coding', 'code the interview', 'flat coding', 'prepare the transcript for analysis', 'code the transcripts in this folder', 'count the codes', 'generate codes', 'run coding on'. Also trigger when the user mentions coding, flat coding, preparing interviews for analysis, or any combination of transcript + codes/analysis — even when the stage is not named explicitly."
---

# Transcript Coding — Flat Coding of Interview Transcripts

Converts a raw interview transcript (JSON array of utterances) into a structured JSON of coded segments suitable for analysis at stage 8 of the pipeline. Default LLM: OpenAI GPT-5.4. Switchable to Claude Opus 4.7 or Gemini per stage via config.

**Contents:** [Scope](#scope) · [Prerequisites](#prerequisites) · [Locating the script](#locating-the-script) · [Workflow](#workflow) · [Quick Reference](#quick-reference) · [When things go wrong](#when-things-go-wrong) · [Design philosophy](#design-philosophy)

---

## Scope

**Does:** four pipeline stages — (1) segmentation of fragmented STT utterances into semantic blocks, (2) global interview pass producing a summary and theme map, (3) per-segment structured coding with core fields + interpretive notes, (4) validation and code-book unification with an accumulative project-wide canonical codebook.

**Does NOT:** transcribe audio (that's `ux-transcribe`), enrich transcripts with screen captures (stage 6 of the research pipeline), or produce analysis/findings (stage 8 — separate skill). Stops at a validated coded JSON.

---

## Prerequisites

Check before the first run. Auto-install what's missing.

**1. OpenAI API key** — required.

Look for `.env` in the current working directory (where the user launched `claude`). Check for `OPENAI_API_KEY`.

If missing, ask the user:
> I need an OpenAI API key. Add a line `OPENAI_API_KEY=sk-...` to the `.env` file in the current folder, or send me the key and I'll add it.

If the user provides the key: `echo "OPENAI_API_KEY=<key>" >> .env`

**2. Python 3.10+** — `python3 --version`.

**3. Python packages:**
```bash
python3 -c "import openai, pydantic, yaml, dotenv" 2>&1
```
On ImportError: `python3 -m pip install -r <skill-path>/scripts/requirements.txt`

**4. Optional backend keys** (only if enabled in config): `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`.

---

## Locating the script

Entry point: `scripts/code_transcript.py` relative to this SKILL.md.

In Claude Code, the user runs `claude` from their project folder. Resolve the skill path and invoke:

```bash
python3 $SKILL_DIR/scripts/code_transcript.py run <transcript.json> <brief.json> --respondent-id <id>
```

---

## Workflow

### 1. Parse the request and locate files

Typical invocations: "code `TICKET-123`" (folder) or a specific file path.

Find:
- **Transcript(s)**: JSON files matching `[{start, end, speaker, text}, ...]` — output of `ux-transcribe`. Usually under `<folder>/transcripts/json/`. Filename (minus extension) becomes the `interview_id`.
- **Brief**: `brief.json` with research questions, hypotheses, respondent metadata. Usually at the root of the interview folder. Schema in `examples/input_brief.json`.
- **Project codebook** (optional): `project_codebook.json` at project root. If absent, gets created at first interview and grows from there.

If the brief is missing, **do not invent one** — ask the user. Without it, mapping to research questions (a core schema field) cannot be produced.

### 2. Check configuration

If `transcript-coding.yaml` exists in CWD, use it. Otherwise fall back to `config.default.yaml` in the skill root. See `references/config_reference.md`.

Surface these to the user before running:
- Backend and model per stage
- Path to the project codebook
- Vision mode (`always` / `triggered` / `never`)

### 3. Summarize and confirm

Show the user:
```
Found in TICKET-123/transcripts/json/:
  • interview_01.json (47 min, 892 utterances)
  • interview_02.json (32 min, 654 utterances)

Brief: TICKET-123/brief.json (6 research questions, 3 hypotheses)
Project codebook: TICKET-123/project_codebook.json (empty — I'll create it on the first interview)
Config: OpenAI GPT-5.4 for the coding stage, mini for the rest.

Estimated time: 3–5 minutes per interview. Starting now.
```

### 4. Run the pipeline

Single interview:
```bash
python3 $SKILL_DIR/scripts/code_transcript.py run <transcript.json> <brief.json> --respondent-id <id>
```

Folder batch:
```bash
python3 $SKILL_DIR/scripts/code_transcript.py run-batch <folder>
```

Script checkpoints after each stage and resumes from checkpoints on re-run (unless `--fresh` is passed).

**Long runs** (>3 files or any file >45 min) — run in background:
```bash
nohup python3 $SKILL_DIR/scripts/code_transcript.py run-batch <folder> > /tmp/coding.log 2>&1 &
echo "PID: $!"
```
Monitor with `tail -f /tmp/coding.log`.

### 5. Inspect results

On success, report:
```
Done! Coded 5 interviews.
  ✅ TICKET-123/transcripts/json/interview_01.coded.json (187 segments)

Project codebook updated: 342 unique codes (48 new).
Validation warnings: 3 (see TICKET-123/transcripts/json/interview_01.validation.md)
```

If warnings exist, offer to show the `<interview-stem>.validation.md` file written next to the coded file.

### 6. Propose the next step

> Next step — the analysis stage (`13-axial-coding`). It takes these codes + the codebook and builds axes, a model, and findings. Run it?

---

## Quick Reference

Load these files **only when you need them** — not upfront.

| Task | Files to read |
|---|---|
| Standard run | this file (Workflow section) |
| Understand output format | `references/json_schema.md` |
| Edit core coding prompt | `references/prompt_local_coding.md` + `references/interpretive_frames.md` |
| Edit segmentation prompt | `references/prompt_segmentation.md` |
| Edit global-pass prompt | `references/prompt_global_pass.md` |
| Edit unification prompt | `references/prompt_unification.md` |
| Change models / switch backend | `references/config_reference.md` + `references/model_backends.md` |
| Debug a failure | `references/troubleshooting.md` |
| Validate a prompt change | `tests/README.md` (golden-fixture regression) |
| See input/output examples | `examples/` |

---

## When things go wrong

First check the script's stderr output (or `/tmp/coding.log` if you used the `nohup` background example above) and `coding/*.validation.md`. Common cases covered in `references/troubleshooting.md` (JSON parse failures, citation mismatches, rate limits, timeouts, `.env` issues).

For reproducible failures not in troubleshooting — save the log and the stage it failed on; that's the input for improving the skill.

---

## Design philosophy

- **Prompts live in `references/*.md`**, not hardcoded in Python — researchers edit them without touching code.
- **Checkpoints after each stage** — re-run only what broke.
- **Accumulative codebook** — consistency grows across interviews rather than suffering from synonyms.
- **Two-tier schema**: core fields validated strictly; interpretive notes use soft validation — they're an analysis aid, not a source of truth.
- **Backend abstraction** — OpenAI / Anthropic / Gemini swappable per stage via config.
