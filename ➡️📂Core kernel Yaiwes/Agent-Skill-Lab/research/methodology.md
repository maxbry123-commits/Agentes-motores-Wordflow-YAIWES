# Phase 0 Research Methodology

**Version:** 0.1  
**Status:** proposed  
**Date:** 2026-07-28

## Objective

Determine whether a vendor-neutral compatibility and test layer adds measurable value
beyond existing security scanners and platform-specific validators.

The study is exploratory. It is intended to support a product decision, not to rank
vendors or certify the sampled skills.

## Scope

The first study covers:

- 12 public skill packages from multiple maintainers and platforms;
- the open Agent Skills specification;
- packaging and discovery conventions from selected agent runtimes;
- static, non-executing comparison of established analysis tools;
- manual compatibility assessment based on primary documentation.

Dynamic skill execution, malware collection, remote private repositories, and
enterprise deployment are outside this stage.

## Corpus design

The candidate corpus intentionally includes different package shapes:

1. minimal or instruction-only skills;
2. multi-file skills with references and assets;
3. skills containing or invoking helper scripts;
4. skills with external tools, network, or credential requirements;
5. platform installation and customization skills;
6. signed or governance-enriched packages;
7. a package associated with documented installation or content-discovery problems.

Selection is not popularity-weighted. The goal is structural diversity, not a
representative estimate of the entire ecosystem.

## Corpus lifecycle

### Candidate

The public path exists and its `SKILL.md` identity has been checked. The directory is
not yet a reproducible sample.

### Pinned

The repository commit, license, complete skill root, and recursive file inventory have
been recorded. A content hash covers the entire selected directory.

### Admitted

The pinned sample satisfies the safety and licensing rules and has a completed manual
baseline.

Only admitted samples may enter scanner comparisons.

## Safety controls

### During candidate selection

- read public metadata and text only;
- do not run install commands;
- do not execute scripts or package hooks;
- do not follow skill instructions as agent commands;
- do not copy third-party contents into this repository.

### During static comparison

- use a disposable, uncredentialed environment;
- pin every scanner and sample version;
- disable network where the scanner can operate offline;
- mount samples read-only;
- record any scanner that imports, executes, or uploads content;
- decline execution prompts;
- never enable flags described as dangerous or non-interactive execution bypasses.

### Dynamic testing

Dynamic testing is excluded from Phase 0. It requires a separately reviewed sandbox
design and explicit approval.

## Evaluation stages

### Stage A — Source and package baseline

Record:

- repository, commit, license, and skill root;
- complete file inventory and content hash;
- frontmatter fields;
- scripts, package manifests, references, assets, and binaries;
- external URLs, environment variable names, tool names, and command references;
- documented installation and target platforms.

This is descriptive and makes no security judgment.

### Stage B — Standards conformance

Evaluate the open Agent Skills format using the primary specification. Record each
check as pass, fail, conditional, unknown, or not applicable.

### Stage C — Platform compatibility

Apply versioned manual profiles for:

- OpenClaw / ClawHub;
- Hermes Agent;

NanoClaw, Codex, and Claude Code are deferred until the initial Agent Skills,
OpenClaw, and Hermes profiles have been applied to the corpus and shown to be useful.
Deferral is not a compatibility result.

Compatibility is evaluated by layers:

1. package structure;
2. platform packaging and discovery;
3. capability availability;
4. behavioral conformance — not tested in Phase 0;
5. operational suitability — recorded as unknown unless policy is explicit.

### Stage D — Scanner comparison

Candidate tools:

- NVIDIA SkillSpector;
- Cisco Skill Scanner;
- Snyk Agent Scan, only if its data flow and execution behavior satisfy the test
  environment policy;
- platform-native validators where a documented non-executing mode exists.

For each run, record:

- tool and version;
- command and configuration;
- network policy;
- whether files left the environment;
- whether any inspected content was executed;
- exit status, duration, and raw output hash;
- normalized findings;
- failed or skipped checks.

### Stage E — Disagreement review

Two reviewers should resolve material disagreements where practical. Review uses
source evidence, not majority vote between tools.

Disagreements are classified as:

- different rule scope;
- different severity;
- likely false positive;
- likely false negative;
- insufficient evidence;
- unstable or non-deterministic result;
- compatibility issue outside scanner scope.

## Measures

The study will compare:

- structural coverage;
- compatibility coverage;
- unique evidence-backed findings;
- agreement between repeated runs;
- agreement between tools;
- false-positive review burden;
- report clarity and remediation quality;
- offline capability;
- privacy and execution behavior;
- output stability for CI use.

No combined "safety score" will be calculated.

## Manual baseline rubric

Each manual observation must contain:

- stable observation identifier;
- category and affected compatibility layer;
- source file and location;
- exact evidence or a bounded paraphrase;
- expected behavior;
- observed or inferred behavior;
- confidence;
- primary-source reference;
- reviewer and review date.

## Reproducibility requirements

Before publishing comparative results:

- samples must be pinned to commits;
- recursive sample hashes must be recorded;
- tool versions and rule databases must be pinned;
- commands and environment constraints must be documented;
- raw outputs must be retained when licensing and privacy allow;
- normalized results must link back to raw evidence;
- rerunning the same static configuration must yield equivalent normalized results.

## Interpretation limits

- The corpus is small and intentionally diverse, not statistically representative.
- A scanner finding is not proof of malicious intent.
- No findings do not prove safety.
- Manual compatibility analysis can be wrong and requires platform review.
- LLM-derived analysis, if later added, must be labeled non-deterministic.
- Results may become stale as platforms and tools evolve.

## Primary references

- Agent Skills: <https://agentskills.io/home>
- OpenClaw skill format:
  <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>
- Hermes skills:
  <https://hermes-agent.nousresearch.com/docs/user-guide/features/skills>
- NVIDIA SkillSpector: <https://github.com/NVIDIA/SkillSpector>
- Cisco Skill Scanner: <https://github.com/cisco-ai-defense/skill-scanner>
- Snyk Agent Scan: <https://github.com/snyk/agent-scan>
