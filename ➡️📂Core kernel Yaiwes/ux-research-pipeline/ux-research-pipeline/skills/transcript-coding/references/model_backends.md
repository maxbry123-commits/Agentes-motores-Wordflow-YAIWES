# Model backends

The pipeline is written against an abstract `LLMBackend` in `scripts/backends/base.py`. Three implementations: `openai_backend.py` (default, GPT-5.4 family), `anthropic_backend.py` (Claude Opus 4.7 / Haiku 4.5), `gemini_backend.py` (Gemini).

Select per stage in `config.yaml` under `stages.<stage>.backend`.

**Contents:** [OpenAI](#openai-default) · [Anthropic](#anthropic-claude) · [Gemini](#gemini) · [Adding a new backend](#adding-a-new-backend) · [Choosing a model](#choosing-a-model-for-your-project)

---

## OpenAI (default)

**Requires:** `OPENAI_API_KEY` in `.env`.

**Recommended models (as of 2026-04):**

| Stage | Model | Why |
|---|---|---|
| segmentation | `gpt-5.4-mini` | Cheap, fast, simple task |
| global_pass | `gpt-5.4-mini` | Summary over a long transcript |
| local_coding | `gpt-5.4` | Complex structured output, needs quality |
| unification | `gpt-5.4-mini` | Clustering synonyms is cheap |

**Reasoning effort** is passed directly via `reasoning_effort`. Values: `none`, `low`, `medium`, `high`, `xhigh`. Only GPT-5.4 family and o-series use it.

**Structured output** via `response_format={"type": "json_schema", "json_schema": {..., "strict": true}}`. Constrains the model to schema-conforming JSON.

**Vision** — native via `image_url` content blocks.

---

## Anthropic (Claude)

**Requires:** `ANTHROPIC_API_KEY` in `.env`.

**Recommended models:**

| Stage | Model |
|---|---|
| segmentation | `claude-haiku-4-5-20251001` |
| global_pass | `claude-haiku-4-5-20251001` or `claude-opus-4-7` for quality |
| local_coding | `claude-opus-4-7` |
| unification | `claude-haiku-4-5-20251001` |

**Reasoning effort** — Anthropic does not expose `reasoning_effort`; the parameter is accepted and silently dropped. Extended thinking is a future TODO (separate config key and API path).

**Structured output** — no native strict JSON-schema mode. The backend uses a **prefilled assistant turn** (`{`) plus the schema in the system prompt, then parses with a balanced-brace scanner. Works reliably but is slightly weaker than OpenAI's strict mode — expect a somewhat higher retry rate on complex schemas.

**Vision** — base64 image blocks.

---

## Gemini

**Requires:** `GOOGLE_API_KEY` in `.env`.

**Models:** current `gemini-*` identifiers — check Gemini docs. The Gemini 2.5 family has strong structured output and very long context (up to 2M tokens for top tier), attractive for very long transcripts.

**Reasoning effort** — not applicable, ignored.

**Structured output** — native JSON schema via `response_schema` in the generation config.

**Vision** — native multimodal input.

---

## Adding a new backend

1. Create `scripts/backends/<name>_backend.py` with a class subclassing `LLMBackend`.
2. Implement `complete()` matching the signature in `base.py`.
3. Add the name to `make_backend()` in `scripts/backends/__init__.py`.
4. Handle auth via environment variables — never accept keys as CLI args.

If the backend lacks structured output, either (a) construct the prompt to emit JSON and parse defensively, or (b) raise `NotImplementedError` when `response_schema` is passed.

---

## Choosing a model for your project

- **Cost-constrained, quality "good enough"**: `gpt-5.4-mini` everywhere.
- **Quality-constrained on OpenAI**: `gpt-5.4` with `reasoning_effort: high` on `local_coding`.
- **Claude-only shop**: `claude-opus-4-7` on `local_coding`; accept a slightly higher retry rate.
- **Very long transcripts** (>2h): Gemini on `global_pass` to fit the whole thing in one call.
