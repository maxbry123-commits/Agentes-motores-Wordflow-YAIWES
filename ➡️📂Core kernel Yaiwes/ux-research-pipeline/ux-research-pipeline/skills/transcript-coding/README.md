# transcript-coding

A Claude Code skill (Cowork-friendly) for **stage 7 of the UX research pipeline — flat coding of in-depth interview transcripts**.

**Contents:** [TL;DR](#tldr) · [Install & run](#install--run) · [Architecture](#architecture) · [Backends](#backends) · [Layout](#layout) · [Design choices](#design-choices) · [Status](#status)

## TL;DR

**In:** raw `ux-transcribe` JSON + a brief with research questions.
**Out:** structured JSON with verbatim quotes, subject codes, content types, mapping to research questions, interpretive notes. Ready for stage 8 analysis.

**Input shape:**
```json
[
  {"start": 1.1, "end": 5.2, "speaker": "Interviewer", "text": "..."},
  ...
]
```

**Output shape:**
```jsonc
{
  "interview_id": "...",
  "project_id": "TICKET-123",
  "global_context": { "summary": "...", "themes": [...], ... },
  "segments": [
    {
      "quote": "verbatim quote from the transcript",
      "subject_codes": ["checkout without prompts", "distrust of a short review"],
      "content_type": "problem",
      "research_question_ids": ["rq_2"],
      "hypothesis_support": [{"hypothesis_id": "h_1", "direction": "against", "note": "..."}],
      "interpretive_notes": "...",
      ...
    }
  ]
}
```

## Install & run

Designed to run from a project folder containing `.env` with API keys.

```bash
# 1. Drop the skill folder wherever convenient (e.g. ~/.claude/skills/transcript-coding/)
# 2. In your project folder:
echo "OPENAI_API_KEY=sk-..." > .env
pip install -r <skill-path>/scripts/requirements.txt

# 3. Single interview
python3 <skill-path>/scripts/code_transcript.py run \
    interviews/TICKET-123/transcripts/json/interview_01.json \
    interviews/TICKET-123/brief.json \
    --respondent-id r_1

# 4. Batch — whole folder
python3 <skill-path>/scripts/code_transcript.py run-batch interviews/TICKET-123/
```

In Claude Code, just say "code the transcripts in TICKET-123" — the skill auto-locates the brief, transcripts, and project codebook.

## Architecture

Four stages with checkpoints after each:

1. **Segmentation** (`gpt-5.4-mini`) — aggregates short STT utterances into coherent 30–90s semantic blocks.
2. **Global pass** (`gpt-5.4-mini`) — interview summary, theme map, through-lines. Used as context for stage 3.
3. **Local coding** (`gpt-5.4`) — per-segment structured output with verbatim-quote validation, subject codes, content type, research-question mapping, interpretive notes.
4. **Validation & unification** — consistency checks + proposed merges of synonymous codes into a canonical project codebook.

## Backends

Default: OpenAI GPT-5.4 throughout. Switchable per stage to Claude (Anthropic) or Gemini via `config.yaml`. See `references/model_backends.md`.

```yaml
# Example: use Claude Opus 4.7 for coding, keep mini-tier for the rest
stages:
  local_coding:
    backend: anthropic
    model: claude-opus-4-7
```

## Layout

```
transcript-coding/
├── SKILL.md                    # entry point for Claude
├── config.default.yaml         # default config
├── README.md                   # this file
├── references/
│   ├── interpretive_frames.md  # 3 presets of hermeneutic lenses
│   ├── prompt_*.md             # per-stage prompts (edit without touching code)
│   ├── json_schema.md          # output schema reference
│   ├── config_reference.md     # config reference
│   ├── model_backends.md       # OpenAI / Anthropic / Gemini
│   └── troubleshooting.md
├── scripts/
│   ├── code_transcript.py      # CLI with 7 subcommands
│   ├── prompt_loader.py
│   ├── schemas/                # Pydantic models
│   ├── backends/               # LLM backend abstractions
│   └── pipeline/               # 5 modules: segmentation, global_pass,
│                                  local_coding, validation, unification
├── examples/                   # example transcript, brief, golden output
└── tests/
    ├── test_schemas.py         # smoke tests (no API)
    ├── compare.py              # regression diff vs golden
    └── golden/                 # golden fixtures
```

## Design choices

- **Prompts in `references/*.md`**, not in Python — researchers edit them without code.
- **Two-tier schema**: core fields (quote, codes, mapping) strict; `interpretive_notes` soft.
- **Checkpoints after each stage** — re-run only what broke.
- **Accumulative project codebook** — consistency grows across interviews.
- **Exact-match citation validation** (normalized by default) catches model hallucinations.
- **Backend abstraction** — switch OpenAI / Anthropic / Gemini in config, no code edits.

## Status

- ✅ Architecture and all pipeline modules
- ✅ Three backends (OpenAI default, Anthropic, Gemini)
- ✅ Three interpretive-frames presets (minimal / default / full)
- ✅ Structured output via Pydantic + JSON Schema
- ✅ Citation validation (three modes: exact / normalized / fuzzy)
- ✅ Minimal regression tests
- ✅ Complete reference docs
- ⏳ Prompts not calibrated on real interviews — needs a couple of iterations on live data
- ⏳ `apply-unification` subcommand to merge approved codebook proposals (only proposal generation so far)
- ⏳ Expand the golden-fixture set for serious regression coverage
