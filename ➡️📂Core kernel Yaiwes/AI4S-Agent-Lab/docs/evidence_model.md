# Evidence model

## Why one log is not enough

A language-model log can show that a call occurred and what text was returned. It cannot, by itself, prove that a scientific tool ran, that a candidate came from that call, that forbidden data was never accessed, that an artifact is valid, or that a scientific conclusion is correct.

The historical project therefore needs a layered evidence chain:

```text
runtime call/stage record
  + source-code control path
  + scientific tool output
  + deterministic validator
  + artifact identity
  + version/platform record
```

The public repository exposes this model without publishing sensitive raw logs.

## Evidence levels

| Level | Evidence | Supports | Does not support by itself |
|---|---|---|---|
| E0 | Narrative claim | a question to investigate | implementation or result |
| E1 | Planner/stage event | an action was proposed or recorded | tool execution or correctness |
| E2 | Code path + deterministic state | defined behavior exists for a version | that it ran in a scored image |
| E3 | Tool output + validator + artifact reference | a concrete execution produced a checked artifact | broad causal improvement |
| E4 | Same-version A/B or repeated runs | local causal or stability evidence under stated conditions | transfer to new domains |
| E5 | Immutable version/log/output/platform binding | strongest historical result identity | scientific truth beyond the metric |

An evidence level is claim-specific. A run can be E5 for “this version received this platform score” and only E1 for “the LLM caused the improvement.”

## Event model

The public trace schema links five event families:

| Event | Required content |
|---|---|
| `observation` | measured fact, source, time/budget scope |
| `proposal` | bounded action, rationale, expected signal, falsifier |
| `tool_result` | tool identity, input reference, output reference, exit status, metrics |
| `verification` | checks performed, result, comparable baseline |
| `decision` | promote, reject, retry, switch, roll back, or stop; reason |

Every event should distinguish data from interpretation.

## Reconstructed traces

Raw competition logs are excluded. The trace examples under `evidence/reconstructed_traces/` are composed from public-safe facts that were supported by code paths, tool-stage records, version notes, and platform outcomes.

They are intentionally labeled:

```json
{
  "reconstructed": true,
  "not_original_log": true,
  "evidence_basis": ["code_path", "stage_record", "version_record"]
}
```

They must not be cited as verbatim runtime output or used to claim fields that were absent from the original evidence.

## Claim checklist

Before publishing a conclusion:

1. What exactly is the claim?
2. Which version and task does it cover?
3. What is the highest evidence level for that exact claim?
4. Is the metric faithful to the stated scientific objective?
5. Is there a same-scale comparison or only correlation?
6. What alternative explanation remains?
7. What would falsify the claim?
8. Is a reconstructed artifact clearly labeled?

The goal is not to eliminate uncertainty. It is to make uncertainty legible.
