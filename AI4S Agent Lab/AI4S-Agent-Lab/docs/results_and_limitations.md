# Results and limitations

## Historical result table

| Track | Reported platform result | Normalized score | Version/evidence boundary |
|---|---:|---:|---|
| Virtual screening | Mean EF1% `39.70` | `0.8095` | Best recorded result `39.69658`, associated with the historical v200 line. A later audit-material correction ran `39.63083`; it did not replace the identity of the best-scoring version. |
| Targeted molecule design | `0.7575` | `0.8339` | The recoverable source-level v115c → v115ga config contrast adds only `GOAL_AWARE_FRAGS=1`. The score record is cross-version, `v115=0.752650` → `v115ga=0.757559` (`+0.004909`, noise-scale), while v115c lacks an independently scored platform run. Different baselines, missing score-bound carriers, and absent repeated equal-budget runs prevent a stable independent-effect estimate. Later audit-hardening was not independently shown to reproduce the score. |
| Protein conformational ensemble | `0.7355` | `0.9075` | Best records `0.735478/0.735239` came from an incompletely seeded line. Two later seeded runs were `0.720025/0.719021`. The best score is not attributed to successful online LLM control. |
| Neural-operator PDE | `176.46 → 88.23` | `0.5181` | Two prebuilt task-specific training tools were ruled out of bounds. Both the KS and cylinder subtasks were halved. This retrospective preserves the ruling without reframing it as success. |

The historical team project's combined score was `1.7414 = 0.9075 + 0.8339`, using the two strongest normalized tracks. Its reviewed rank was 6, which advanced that project to the final. These are not presented as the author's individual results.

## Claims supported by the record

- Four task-specific systems applied a common research-control discipline at different depths.
- Real runtime measurements affected task1 scheduling and execution depth.
- In task2, docking results from the current target affected later candidate generation through feedback-driven fragment weighting.
- Task3 generated structures from new sequence/MSA-conditioned computation and selected an ensemble under quality/diversity constraints.
- Later task-specific versions implemented supervisor-style review, but the review was advisory and not a universal independent-agent security boundary.
- Task4 demonstrates that real runtime training and a ReAct controller do not excuse a prebuilt tool that already contains the task-specific scientific answer.

## Claims not supported

- One frozen universal agent solved all four domains without adaptation.
- All four tasks used the same runtime model, same planner, same memory, or same solve runner.
- A named language model caused any highest platform score without a complete immutable version/log/score binding.
- JSONL logs alone prove artifact lineage, scientific correctness, or absence of prohibited access.
- Docking scores equal experimental affinity, drug efficacy, or wet-lab validation.
- A single high score represents a stable distribution.
- The cross-version task2 difference establishes a platform A/B or stable `+0.004909` independent effect for `GOAL_AWARE_FRAGS=1`.
- This personal public repository can rebuild the original scoring images or repeat official results.
- The task4 penalty was limited to one subtask, or was cancelled by the fact that training happened at runtime.

## Why score and reproducibility are separate

At least four objects existed during the project:

1. the image that received a platform score;
2. a later code-review package;
3. the post-competition working tree;
4. historical experiments and patches.

They are related, but not byte-identical. A platform number must remain attached to the evidence level and version identity that actually support it.

## Scientific limitations

- Competition metrics are proxies for broader scientific utility.
- Molecular docking and route-search outputs need experimental validation before real-world claims.
- Protein-ensemble metrics do not fully establish biological ensemble fidelity.
- Neural-operator competition evaluation does not establish general PDE-method superiority.
- Time-limited agent behavior is sensitive to hardware throughput, online-service availability, randomness, and fallback paths.

## Publication limitations

The public repository excludes official inputs, predictions, checkpoints, original logs, submission archives, private base images, internal services, and source with unresolved third-party provenance. These exclusions are part of responsible publication, not evidence that the historical work did not occur.

## Public v0.1 implementation limitations

- The executable is POSIX-only for R2: evidence locking uses `fcntl`, and durability assumes same-filesystem atomic replace plus `fsync`.
- The only built-in budget is a fixed iteration count; deadline, timeout, delivery reserve, checkpoint, and resume policies remain future work.
- The loop keeps and defensively copies complete in-memory history each round. That favors inspectability for short examples but grows approximately quadratically and is not a long-run memory design.
- The deterministic validator checks declared numeric constraints; it is not a domain-science oracle.
- The synthetic example demonstrates control and evidence mechanics, not autonomous discovery in one of the four historical domains.
