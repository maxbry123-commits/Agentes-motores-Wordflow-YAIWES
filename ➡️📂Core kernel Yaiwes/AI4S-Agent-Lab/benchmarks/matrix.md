# Public benchmark matrix

Status values:

- `READY` — fixture and metric exist and have passed the current publication audit.
- `PLANNED` — specified but not yet implemented or run.
- `OUT_OF_SCOPE` — requires excluded historical assets.

| Benchmark | Purpose | Status | Public evidence |
|---|---|---|---|
| Synthetic happy path | valid candidate promotes over floor | READY | unit/e2e tests + manifest |
| Invalid candidate | validator blocks promotion | READY | Before → Action → After, lineage, non-finite, and strict-contract assertions |
| Tool failure | controller retains floor and records failure | READY | exception and extreme-score fault-injection tests |
| Atomic delivery | interrupted candidate write cannot corrupt accepted artifact | READY | replacement-failure and canonical read-back tests |
| Context truncation | required evidence survives bounded context selection | PLANNED | source-retention metric |
| Reviewer independence | reviewer catches failures beyond deterministic baseline under same budget | PLANNED | same-budget ablation |
| Cross-run memory | verified record helps without stale contamination | PLANNED | repeated synthetic tasks |
| Historical task1–4 scores | reproduce official results | OUT_OF_SCOPE | R4 not claimed |

The publication audit should change a row to `READY` only after recording the exact command and outcome in [`audit/CURRENT_VERIFICATION.md`](../audit/CURRENT_VERIFICATION.md).
