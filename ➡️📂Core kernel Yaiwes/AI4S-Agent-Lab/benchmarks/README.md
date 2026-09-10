# Benchmark status and evaluation plan

## What was actually benchmarked

The historical systems were evaluated by the competition platform on four scientific tasks. Those platform results are reported in [Results and limitations](../docs/results_and_limitations.md).

## What was not benchmarked

The project did **not** run a recognized open-source general-agent benchmark that established:

- universal scientific-agent capability;
- multi-agent superiority;
- long-term memory quality;
- context-compression quality;
- hallucination rate across tasks;
- transfer to an external unseen scientific benchmark.

References to external scientific-agent benchmarks during reflection were calibration and design inspiration, not results from this system. Reading a benchmark does not mean this project passed it.

## Proposed same-budget benchmark matrix

| Axis | Baselines | Controlled resources | Measures |
|---|---|---|---|
| Control | deterministic workflow; one planner; planner + deterministic verifier; planner + independent reviewer | wall time, tool calls, model tokens | task quality, invalid-output rate, recovery rate |
| Agent count | 1, 2, and larger role sets | same total model/tool budget | quality gain per cost, correlated error, latency |
| Context | recent window; evidence-selected context; compressed summary | same token budget | decision accuracy, source retention, stale-state errors |
| Memory | none; in-run episode; verified cross-run memory | same retrieval budget | transfer, contradiction rate, stale-memory damage |
| Verification | model self-check; deterministic gate; scientific evaluator | same candidate set | false promotion, false rejection, hallucination escape |
| Robustness | normal; tool timeout; malformed output; missing asset; budget pressure | same task fixture | floor survival, rollback correctness, delivery success |

## Required reporting

Every benchmark result should include:

- task and dataset license;
- exact version and configuration;
- number of runs and seeds;
- score center and spread;
- invalid-output and failure rate;
- wall time, model tokens, and scientific-tool cost;
- verifier false-promotion/false-rejection counts where measurable;
- known distribution mismatch;
- R1–R4 level.

## Synthetic benchmark in this repository

The personal synthetic example is an engineering benchmark for contracts, evidence events, promotion, rollback, and atomic delivery. It is **not** a benchmark of molecular design, protein biology, PDE accuracy, or general scientific discovery.

See [benchmark matrix](matrix.md).
