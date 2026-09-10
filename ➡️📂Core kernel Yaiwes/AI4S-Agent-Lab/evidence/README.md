# Public evidence layer

The public evidence layer explains how an observation can be traced to an action, scientific-tool result, verification, and final decision without publishing raw competition logs.

## Important warning

Files under [`reconstructed_traces/`](reconstructed_traces/) are **not original logs**. They are public-safe composite reconstructions based on historical code paths, stage records, version notes, tool-result summaries, and platform outcomes.

Every line contains:

```json
"reconstructed": true,
"not_original_log": true
```

If those fields are removed, the trace is no longer compliant with this repository’s evidence policy.

## Files

- [Trace schema](trace_schema.md)
- [Task1 scheduling and delivery trace](reconstructed_traces/task1_virtual_screening.jsonl)
- [Task2 docking-feedback trace](reconstructed_traces/task2_molecule_design.jsonl)
- [Task3 version and selection trace](reconstructed_traces/task3_protein_ensemble.jsonl)
- [Task4 tool-governance trace](reconstructed_traces/task4_tool_governance.jsonl)

## What reconstructed traces are good for

- teaching the shape of a research loop;
- reviewing which observation is supposed to change which action;
- checking that a conclusion does not exceed its evidence;
- designing future structured runtime logging.

## What they cannot prove

- exact original wording, timestamps, parameters, or action order;
- that one historical run contained every reconstructed field;
- artifact lineage or absence of prohibited access;
- causal effect of a language model;
- reproducibility of a platform score.

See [Evidence model](../docs/evidence_model.md) for evidence levels.
