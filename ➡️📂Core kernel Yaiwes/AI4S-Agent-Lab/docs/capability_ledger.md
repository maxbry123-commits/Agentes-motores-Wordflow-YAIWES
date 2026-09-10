# Capability ledger

This ledger separates **implemented**, **partially implemented**, **evidence-limited**, and **future work**. It prevents a useful architectural idea from being rewritten as a completed historical feature.

Legend:

- **Observed** — supported by a specific historical code path plus compatible records.
- **Partial** — present in some tasks or later versions, with material limitations.
- **Not demonstrated** — no sufficient historical implementation/evidence.
- **Public reference** — represented by personal code or documentation here.

| Capability | Historical status | Evidence and boundary | Public status |
|---|---|---|---|
| Input understanding | Observed | Task-specific input parsing and resource probes; not semantic open-world understanding | Synthetic task-contract example |
| Task decomposition | Partial | Pipelines decomposed work into stages; decomposition was largely designed before runtime | Documented stage pattern |
| Hypothesis proposal | Partial | Bounded LLM proposals in task2/task4; narrower or mostly deterministic control elsewhere | Planner interface, no universal claim |
| Experimental design | Partial | Minimum tests and budget gates existed, but many search spaces and thresholds were predesigned | Documented hypothesis-card pattern |
| Real tool execution | Observed | Scoring, docking, folding, sampling, route search, training, and validation ran in task-specific systems | Interfaces only; backends excluded |
| Feedback changes next action | Observed, uneven | Strong in task2; action/parameter feedback in task4; task1/task3 had narrower decision surfaces | Generic event and gate pattern |
| Multi-round iteration | Observed, uneven | Candidate evolution and training loops existed; depth varied by task and budget | Synthetic loop |
| Same-scale promotion | Partial | Some paths compared candidate and floor with aligned metrics; not a single shared implementation | Verifier-gate primitive |
| Rollback/fallback | Observed | Task-specific floors, degradation paths, and atomic output protection | Personal synthetic rollback example |
| Runtime supervisor | Partial | Later task-specific versions combined deterministic checks with optional LLM review | Not implemented; deterministic validator only |
| Strong multi-agent isolation | Not demonstrated | Roles sometimes shared process, client, context, and authority | Future benchmark item |
| More-agents-is-better | Not demonstrated | No same-budget ablation supports the claim | Explicitly rejected as assumption |
| Context selection | Partial | Some tasks passed aggregated features; one controller retained a bounded recent window | Not implemented; benchmark plan only |
| Context compression | Partial/evidence-limited | Compact status existed in one path; no shared measured compressor | Future evaluation |
| Short-term episodic memory | Partial | In-run state and recent actions existed, without a common memory service | Roadmap |
| Cross-run long-term memory | Not demonstrated at runtime | Development knowledge lived in Git documents and version history | Roadmap only |
| Socratic-question memory | Not demonstrated | No verified runtime store of questions across sessions/runs | Roadmap only |
| Hallucination prevention | Partial | Structured outputs, real tools, deterministic gates, and fallbacks reduced risk; none eliminates hallucination | Layered evidence design |
| Input-scope protection | Partial | Task-specific scans and tool restrictions; supervisors were not formal sandboxes | Release policy and repository scan only |
| Complete artifact lineage | Not demonstrated | Logs and artifacts could be cross-checked, but no cryptographic end-to-end provenance across all tasks | Trace schema with explicit source refs |
| Version provenance | Partial | Stronger in later audits; scoring image, review package, and current source sometimes diverged | File manifest and publication audit |
| Seeded stability | Partial | Task3 later had two seeded runs near `0.72`; best score line was not fully seeded | Repeat-run benchmark design |
| Historical score reproduction | Not demonstrated publicly | Data, weights, images, exact environment, and immutable bindings are incomplete or non-public | R4 not claimed |

## How to use this ledger

When adding a feature or claim:

1. identify the exact capability row;
2. add evidence that measures behavior, not only code presence;
3. state task/version scope;
4. update the reproducibility level;
5. leave the old limitation visible if the new evidence does not fully remove it.

The ledger is intentionally stricter than a marketing feature list.
