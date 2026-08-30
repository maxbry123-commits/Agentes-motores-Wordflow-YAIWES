# Negative-result ledger

The table below records representative failures that materially changed the project. Wanrun Cong curated it from available historical observations; it is not a complete raw experiment dump.

| Area | Hypothesis or change | Observation | Decision and lesson |
|---|---|---|---|
| Input discovery | Enumerating expected directories would find mounted data | The container could start before remote-mounted content appeared in enumeration | Add bounded readiness, direct contract probes, and an empty-input floor; startup success is not input success |
| Artifact delivery | Spending nearly the full budget on inference maximizes score | A run reached delivery close to the hard deadline and did not finish cleanly | Reserve delivery time; valid committed output dominates unfinished computation |
| Virtual-screening conformers | More aggressive low iteration count would increase throughput | Failure rate increased and effective scored throughput did not improve | Revert; optimize successful work per second, not nominal loop speed |
| Virtual-screening fusion | Missing configuration would safely use intended defaults | Wrong defaults allowed an unintended signal to dominate and caused a severe regression | Make effective runtime weights observable and test missing-config behavior |
| “Smarter” task1 variants | More ensemble/debias/refinement logic would beat a simpler line | Many increasingly complex versions failed to improve a long-standing platform peak | Stop feature accumulation; return to clean single-variable evaluation |
| Goal-aware fragments | Current-target docking winners contain useful fragments for the next generation | Source diff toggles only `GOAL_AWARE_FRAGS=1`; the score record is cross-version, `v115=0.752650` → `v115ga=0.757559` (`+0.004909`, noise-scale), while v115c lacks an independently scored platform run | Retain the feedback mechanism; the different-baseline score observation, missing bound carriers, and absent repeated equal-budget runs do not establish a stable independent lift |
| Retrieval-augmented fragments | More historical/retrieved fragment context would improve task2 | Later variant recorded `0.742419` | Reject; current-target evidence beat added context in this comparison |
| Larger final output | Emitting more molecules would improve task2 | Variant recorded approximately `0.706` | Reject; output count is not quality |
| Protein proxy selection | A later anchor-selection variant looked better on a development proxy | Platform result fell to `0.706088` from a nearby `0.735239` line | Reject; the proxy did not represent the evaluation distribution well enough |
| Seeded protein reproducibility | Fixing seed would reproduce the historical `0.7355` | Later repeated version ran near `0.719–0.720` | Report both high point and stable later range; do not promise exact reproduction |
| More scientific-agent freedom | Runtime training plus parameter choice implied autonomous method discovery | Two task-specific training tools already encoded the method and metric alignment | Accept penalty; redefine the atomic-tool boundary |
| Supervisor prompt | A second role could prove compliance | Review roles were advisory and sometimes shared process/client/context | Keep deterministic checks as source of truth; test isolation separately |
| More agents | More roles should improve decisions | No controlled same-budget ablation established this | Treat as an open benchmark question, not a feature claim |
| Long-term memory | Repository knowledge could be described as runtime memory | Development documents persisted, but no cross-run runtime memory service existed | Separate organizational memory from agent memory |

## Reporting rule

A failed experiment stays visible when it changes a decision, a boundary, or a reusable method. It should not be removed merely because it weakens a linear success narrative.

## What is still missing

The historical project did not run a complete, same-budget experimental matrix for:

- deterministic workflow vs single planner vs planner + reviewer vs larger multi-agent system;
- no memory vs short-term episode memory vs evidence-linked long-term memory;
- context window size vs compression quality vs scientific performance;
- hallucination rate under different verifier designs;
- cross-task transfer on a new external benchmark.

Those are proposed future benchmarks, not hidden completed results.
