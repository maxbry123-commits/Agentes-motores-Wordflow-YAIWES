# Iteration timeline

This is a public-safe phase timeline. It deliberately avoids private infrastructure and raw operational logs.

## Phase 1 — establish four independent baselines

The project began with four task-specific pipelines rather than forcing one solver abstraction:

- a full-coverage molecular-screening floor;
- a molecule generation/docking/route pipeline;
- a protein folding/sampling/selection graph;
- a neural-operator training and inference workflow.

The shared harness covered model calls, logging, rules, and basic delivery patterns. The domain algorithms remained separate.

## Phase 2 — learn that execution contracts are scientific bottlenecks

Early virtual-screening submissions exposed failures unrelated to model quality:

- remote-mounted input was not immediately discoverable;
- a container could succeed while producing an empty or invalid artifact;
- output persistence and clean exit consumed real deadline budget;
- local hardware expectations did not predict evaluation throughput.

The response was to add bounded readiness checks, direct input probes, measured throughput, floor-first behavior, atomic archives, independent validation, and explicit delivery reserve.

This changed the project’s definition of an Agent: the system had to reason over operational evidence, not only scientific scores.

## Phase 3 — turn task2 into a real feedback loop

The molecule-design system moved from generate-and-rank toward generate-measure-update:

1. profile the new pocket;
2. generate candidates;
3. run real docking;
4. extract fragments from the current target’s stronger candidates;
5. increase their probability in the next generation;
6. redock and search routes before delivery.

The v115ga line recorded `0.757559`. Later, more elaborate fragment retrieval and larger output variants regressed, so they were not allowed to replace the simpler evidence-backed path.

Version evidence supports the narrower causal statement that docking feedback changed the distribution sampled in a later round. The recoverable historical v115c → v115ga run-config comparison is a source-level single toggle, `GOAL_AWARE_FRAGS=1`. Separately, the historical platform record contains a cross-version observation, `v115=0.752650` → `v115ga=0.757559` (`+0.004909`), and described that magnitude as within evaluation noise. v115c lacks an independently scored platform run, so the score observation is not a platform A/B for the source-level contrast. Because the complete scoring image and score-bound log carriers are also missing and no repeated equal-budget runs estimated variance, the cross-version difference is not a stable independent score-lift estimate.

## Phase 4 — separate protein high point from stable range

The protein pipeline combined folding, MSA-dependent branches, sampling, and diversity selection. Two nearby unseeded versions reached `0.735478` and `0.735239`.

A later anchor-selection change appeared positive on a development proxy but scored `0.706088` on the platform. The proxy did not represent the evaluation distribution well enough, so the change was rejected.

Later seed-controlled versions ran `0.720025` and `0.719021`. The project preserved both statements:

- historical best: approximately `0.7355`;
- later seeded operating center: approximately `0.72`.

It did not rewrite one as the other.

## Phase 5 — discover the tool-governance failure

The PDE controller looked highly agentic: it read curves and validation results, selected actions, trained at runtime, promoted candidates, and rolled back failures.

The review found that two prebuilt tools already contained task-specific training and metric-alignment logic. Both subtasks were halved: `176.46 → 88.23`.

The project’s strongest governance rule came from this failure:

> Review the scientific content of tools, not only the apparent freedom of the planner.

## Phase 6 — version archaeology and evidence repair

During the post-competition review, four objects that had often been described too loosely were separated:

- scoring image;
- later review package;
- current working tree;
- historical experiments.

Results were rebound to the strongest supported version identity. Claims about model brands, seed reproducibility, supervisor coverage, and tool boundaries were narrowed where evidence was incomplete.

## Phase 7 — defense and public reconstruction

The final defense narrative emphasized:

- observation → action → scientific tool → evidence → promotion/rollback;
- different control depth across the four tasks;
- reconstructed logs as evidence aids, not original records;
- the absence of a universal multi-agent runtime or long-term memory service;
- the task4 penalty as a scientific and governance lesson.

After the defense, Wanrun Cong started this personal repository from a new history and redesigned the reusable control code, synthetic experiment, evidence model, and research notes for public study. Historical competition scores remain project-level context only. Original logs, official data, submission artifacts, third-party payloads, and defense materials were not imported.
