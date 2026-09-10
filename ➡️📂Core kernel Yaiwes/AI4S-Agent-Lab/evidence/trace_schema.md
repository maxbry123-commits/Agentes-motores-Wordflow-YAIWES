# Reconstructed trace schema

Each JSONL line is one event.

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `trace_id` | string | Stable public reconstruction identifier |
| `sequence` | integer | Explanatory order, not an original timestamp |
| `event_type` | string | `metadata`, `observation`, `proposal`, `tool_result`, `verification`, `decision`, or `review_outcome` |
| `summary` | string | Public-safe statement of the event |
| `reconstructed` | boolean | Must be `true` |
| `not_original_log` | boolean | Must be `true` |
| `evidence_basis` | array[string] | Kinds of historical evidence used, not private paths |
| `claim_limit` | string | What this event does not establish |

## Recommended fields

| Field | Meaning |
|---|---|
| `observation` | Measured or recorded fact |
| `action` | Bounded next step |
| `expected_signal` | Evidence expected if the hypothesis is correct |
| `tool_family` | Public name of the scientific operation, not internal executable path |
| `result` | Public-safe result summary |
| `verdict` | `promote`, `retain_floor`, `reject`, `retry`, `switch`, `stop`, or `penalized` |
| `version_scope` | Historical version family covered by the reconstruction |
| `reproducibility_level` | R1–R4 level supported by this public artifact |

## Reconstruction rules

1. Never copy a sensitive raw line and call it reconstructed.
2. Do not invent exact timestamps, prompts, parameters, counts, or metrics absent from public-safe evidence.
3. A composite sequence must state that it may combine code, stage, version, and platform evidence.
4. Keep runtime evidence separate from later review outcomes.
5. Do not upgrade an LLM proposal into a tool result.
6. Do not upgrade a deterministic format check into scientific validation.
7. Do not upgrade a platform score into a causal model attribution.
