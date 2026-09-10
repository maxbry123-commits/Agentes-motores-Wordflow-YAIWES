# JSON schema reference

Version: 1.0

Canonical output format of the coding pipeline. Defined in `scripts/schemas/coding.py` (Pydantic). This document is for human reading — the Pydantic source is ground truth.

**Contents:** [Top level](#top-level-codedtranscript) · [GlobalContext](#globalcontext-stage-72-output-embedded) · [CodedSegment](#codedsegment-stage-73-output-one-per-segment) · [CodedSegment example](#codedsegment-example) · [ProjectCodebook](#projectcodebook-accumulative)

---

## Top level: `CodedTranscript`

```jsonc
{
  "interview_id": "interview_01",
  "project_id": "TICKET-123",
  "global_context": { /* GlobalContext — see §2 */ },
  "segments": [ /* array of CodedSegment — see §3 */ ],
  "prompt_versions": {
    "segmentation": "1.0",
    "global_pass": "1.0",
    "local_coding": "1.0",
    "interpretive_frames_preset": "default"
  }
}
```

- `interview_id` — stable identifier of this interview (usually the transcript filename minus extension).
- `project_id` — from the brief.
- `prompt_versions` — which version of each prompt produced this output. Used for regression and for correlating quality with prompt edits.

---

## `GlobalContext` (stage 7.2 output, embedded)

```jsonc
{
  "summary": "5–10 sentences (in the respondent's language) about what this interview is about...",
  "themes": ["checkout without CVC", "trust in reviews", ...],
  "participants": {
    "Interviewer": "interviewer from the research team",
    "Respondent": "active user of the service, age 34"
  },
  "key_tasks": ["test checkout", "describe the last order", ...],
  "notable_dynamics": "Free-form paragraph about remarkable shifts or through-lines."
}
```

Used as shared context when coding each segment. Not directly consumed by the analysis stage.

---

## `CodedSegment` (stage 7.3 output, one per segment)

### Identity fields

- `segment_id` — stable per interview (e.g. `seg_0042`)
- `interview_id` — parent interview
- `timecode_start`, `timecode_end` — seconds (float)
- `guide_block` — string or null

### CORE — the quote

- `quote` — **verbatim** text from the transcript. Validator checks this matches the source (modes: exact / normalized / fuzzy). Length 1–6 sentences.
- `quote_cleaned` — optional cleaned version with hesitations removed.

### CORE — content codes

- `subject_codes` — array of 1–5 flat codes about what the segment is about. In the respondent's language, lowercase (except brand/product names), close to the respondent's wording. No hierarchy, no abstractions.
- `content_type` — one of: `insight` / `problem` / `wish` / `action` / `state` / `process`

### CORE — research alignment

- `research_question_ids` — array of research question IDs (from brief) this segment addresses. May be empty.
- `hypothesis_support` — array of `{hypothesis_id, direction, note}`. Direction ∈ `for` / `against` / `mixed` / `none`.

### CORE — respondent meta

- `respondent_id`, `respondent_segment`, `respondent_city` — copied from the brief at runtime. Never extracted from the transcript.

### CORE — screen state (if present)

- `screen_state` — `{screenshot_ref, description}` or null. Null when the transcript had no screen enrichment.

### NON-CORE — interpretive notes

- `interpretive_notes` — free-text paragraph or bullets (in the respondent's language) applying the hermeneutic lenses from the configured preset. May be null when nothing notable appears. Soft validation only.

### Run metadata

- `meta` — `{model, prompt_version, retries, validation_warnings}`. For debugging and regression. Not consumed by the analysis stage.

---

## `CodedSegment` example

```jsonc
{
  "segment_id": "seg_0042",
  "interview_id": "interview_03",
  "timecode_start": 847.2,
  "timecode_end": 892.5,
  "guide_block": "checkout test",
  "quote": "Well, I rarely do this, but this time I had to, and so I hit 'pay', and it's blank — where to enter anything is unclear.",
  "quote_cleaned": "I rarely do this, but this time I had to. I hit 'pay' and it's blank — where to enter anything is unclear.",
  "subject_codes": ["checkout without prompts", "confusing payment screen"],
  "content_type": "problem",
  "research_question_ids": ["rq_2"],
  "hypothesis_support": [
    {"hypothesis_id": "h_1", "direction": "against",
     "note": "The respondent finds the screen insufficiently clear."}
  ],
  "respondent_id": "r_3",
  "respondent_segment": "active users",
  "respondent_city": "New York",
  "screen_state": null,
  "interpretive_notes": "Speech act — responsibility shedding ('I rarely do this'). Attribution to the system ('it's blank'), not to the respondent's own confusion. Deontic modality ('I had to').",
  "meta": {
    "model": "gpt-5.4-2026-03-05",
    "prompt_version": "1.0",
    "retries": 0,
    "validation_warnings": []
  }
}
```

---

## `ProjectCodebook` (accumulative)

```jsonc
{
  "project_id": "TICKET-123",
  "entries": [
    {
      "canonical": "checkout without prompts",
      "variants": ["confusing payment screen", "unclear what to enter at checkout"],
      "definition": "User cannot tell which fields to fill on the payment screen.",
      "first_seen_interview": "interview_03",
      "occurrences": 7
    }
  ]
}
```

Stored at the project root as `project_codebook.json`. Updated via the `unify` subcommand + researcher review.
