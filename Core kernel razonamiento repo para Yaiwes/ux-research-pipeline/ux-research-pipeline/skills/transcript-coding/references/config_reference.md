# Config reference

The skill loads `config.default.yaml` first, then merges any override from either `--config <path>` or `transcript-coding.yaml` in the current working directory.

**Contents:** [Common override patterns](#common-override-patterns) · [Full key reference](#full-key-reference)

---

## Common override patterns

### 1. Cost optimization — cheap stages on mini

Already the default. Only `local_coding` uses full `gpt-5.4`; others use `gpt-5.4-mini`.

### 2. Switch to Claude for everything

```yaml
stages:
  segmentation:
    backend: anthropic
    model: claude-haiku-4-5-20251001
    reasoning_effort: none
  global_pass:
    backend: anthropic
    model: claude-opus-4-7
    reasoning_effort: none
  local_coding:
    backend: anthropic
    model: claude-opus-4-7
    reasoning_effort: none
  unification:
    backend: anthropic
    model: claude-haiku-4-5-20251001
    reasoning_effort: none
```

Requires `ANTHROPIC_API_KEY` in `.env`. Claude ignores `reasoning_effort` — the parameter is passed but silently dropped. See `model_backends.md`.

### 3. Mixed: GPT-5.4 for coding, Claude for global pass

```yaml
stages:
  global_pass:
    backend: anthropic
    model: claude-opus-4-7
```

Everything else stays at defaults — that's the point of the override merge.

### 4. Reduce recent-context window for faster coding

```yaml
local_coding:
  context_window_size: 1   # was 3
  max_retries: 2           # was 3
```

### 5. Switch interpretive preset

```yaml
local_coding:
  interpretive_preset: minimal         # or full, or custom:/abs/path/to/frames.md
```

---

## Full key reference

All keys, in order.

### `stages.*`

For each of `segmentation`, `global_pass`, `local_coding`, `unification`:

- `backend` — `openai` | `anthropic` | `gemini`
- `model` — backend-specific model identifier
- `reasoning_effort` — `none` | `low` | `medium` | `high` | `xhigh` (OpenAI only)
- `max_completion_tokens` — integer

### `local_coding`

- `context_window_size` — how many preceding coded segments pass as recent context (0–10)
- `max_retries` — per-segment retry budget (0–5)
- `interpretive_preset` — `minimal` | `default` | `full` | `custom:<path>`

### `vision`

- `mode` — `always` | `triggered` | `never`
- `trigger_words` — list of words activating vision in `triggered` mode

### `segmentation`

- `target_duration_seconds` — guidance for average segment length
- `max_duration_seconds` — cap; the prompt is told not to exceed
- `min_duration_seconds` — floor; shorter blocks merged forward

### `validation`

- `citation_match_mode` — `exact` | `normalized` | `fuzzy`
  - `exact`: strict substring. Rejects any paraphrase.
  - `normalized` (default): lowercase + punctuation / whitespace normalized. Accepts case and punctuation edits, rejects word substitutions.
  - `fuzzy`: SequenceMatcher ratio. Accepts minor word edits below the threshold.
- `fuzzy_threshold` — float 0.0–1.0
- `on_citation_mismatch` — `retry` | `warn` | `fail`

### `unification`

- `similarity_threshold` — informational only, passed to the prompt
- `require_human_review` — if true, emit a CSV proposal; nothing auto-merged

### `paths`

- `coding_subdir` — subdirectory inside the interview folder for intermediate artifacts
- `codebook_filename` — filename of the project-wide codebook JSON in the project root

### `logging`

- `level` — `DEBUG` | `INFO` | `WARNING` | `ERROR`
- `log_llm_calls` — if true, writes full request/response to the run log (expensive)
