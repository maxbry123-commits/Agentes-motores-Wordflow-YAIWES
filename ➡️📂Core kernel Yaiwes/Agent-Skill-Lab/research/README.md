# Research

Phase 0 exists to test the Agent Skill Lab product thesis before implementation.

## Current artifacts

- [Methodology](methodology.md) — how samples and tools will be compared safely.
- [Admitted corpus](corpus.yml) — 12 public skill packages pinned for research.
- [Complete inventories](inventories.yml) — immutable tree and file identities.
- [Admission report](admission-001.md) — pinning, licensing, and replacement decisions.
- [Result schema](result-schema.md) — common structure for normalized observations.
- [Compatibility profiles](profiles/README.md) — versioned rules derived from primary
  platform documentation.
- [Manual compatibility results](results/README.md) — rule-level static baselines for
  admitted samples.
- [SkillSpector differentiation check](skillspector-comparison-001.md) — pinned
  documentary comparison and go-or-stop execution gate.
- [SkillSpector differentiation execution](skillspector-execution-001.md) — isolated
  offline run, result comparison, and provisional product decision.
- [Initial observations](findings-001.md) — evidence gathered before running scanners.
- [Fixture policy](fixtures/README.md) — rules for future controlled test fixtures.

## Current status

The corpus contains **12 admitted samples** pinned to immutable repository commits.
Their 103 files have complete Git inventories and independent inventory hashes.

No skill in the corpus has been installed or executed by this project.

Manual compatibility baselines are complete for **3 of the 12 admitted samples**:
`ASL-C004` (`handoff`), `ASL-C005` (`autoreview`), and `ASL-C007` (`llm-wiki`).
Nine samples remain.

## Workboard

1. [Pin and admit the initial 12-skill corpus](https://github.com/ricardoml96/agent-skill-lab/issues/1)
2. [Create manual compatibility baselines](https://github.com/ricardoml96/agent-skill-lab/issues/2)
3. [Compare existing scanners safely](https://github.com/ricardoml96/agent-skill-lab/issues/3)
4. [Draft the normalized capability taxonomy](https://github.com/ricardoml96/agent-skill-lab/issues/4)

## Research questions

1. Which structural and packaging failures are missed by security-first scanners?
2. How often do scanners disagree, and do their reports include enough evidence to
   resolve the disagreement?
3. Can capabilities be normalized across platforms without implying enforcement?
4. Which compatibility claims can be checked deterministically and offline?
5. Which report fields are stable enough for CI and long-term comparison?
6. Do authors value conformance and portability checks enough to adopt them?

## Decision gate

Implementation begins only if research demonstrates:

- at least three repeatable compatibility or quality problems;
- at least two meaningful disagreements between existing tools, or equivalent gaps;
- at least one useful check that can run deterministically, locally, and without
  executing the inspected skill.

If these conditions are not met, the project scope must be changed before code is
written.

## Safety

Research follows the repository [Threat Model](../docs/threat-model.md).

- Static inspection comes before execution.
- Public URLs are references, not trust endorsements.
- No live malware is added to the repository.
- No third-party code is executed on a personal or credentialed host.
- Any future scanner execution must use pinned versions and a disposable environment.
