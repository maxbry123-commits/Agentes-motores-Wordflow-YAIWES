# SkillSpector Differentiation Check

**Status:** documentary comparison; scanner not executed
**Review date:** 2026-07-30
**Decision:** execution experiment required before continuing the corpus baseline

## Decision question

Does Agent Skill Lab identify useful, repeatable compatibility problems that NVIDIA
SkillSpector does not already report?

This checkpoint prevents the project from spending time on nine further manual
baselines before its differentiation has been demonstrated.

## Pinned comparison target

- Repository: `NVIDIA/SkillSpector`
- Version: `2.5.0`
- Commit: `34f60308522f45447cd343da0aad77bcea308ad4`
- Commit date: 2026-07-27
- License: Apache-2.0
- Evaluation mode: documentary and static source inspection only

Primary sources:

- [README at the pinned commit](https://github.com/NVIDIA/SkillSpector/blob/34f60308522f45447cd343da0aad77bcea308ad4/README.md)
- [2.5.0 release notes](https://github.com/NVIDIA/SkillSpector/blob/34f60308522f45447cd343da0aad77bcea308ad4/docs/release/skillspector-2.5.0.md)
- [Pinned package metadata](https://github.com/NVIDIA/SkillSpector/blob/34f60308522f45447cd343da0aad77bcea308ad4/pyproject.toml)
- [Apache-2.0 license](https://github.com/NVIDIA/SkillSpector/blob/34f60308522f45447cd343da0aad77bcea308ad4/LICENSE)

No SkillSpector package, command, analyzer, model, URL input, or scanner workflow was
installed or executed for this checkpoint.

## Confirmed SkillSpector scope

The pinned documentation describes:

- 68 vulnerability patterns across 17 categories;
- local files, directories, archives, URLs, and Git repositories as inputs;
- regex, Python AST, YARA, taint, supply-chain, and optional LLM analysis;
- missing, underdeclared, wildcard, and overdeclared capability checks;
- LLM-backed description-versus-behavior comparison;
- terminal, JSON, Markdown, and SARIF output;
- evidence locations, confidence, remediation, and risk recommendations;
- fingerprinted false-positive baselines;
- CI exit codes and an MCP install-gate integration;
- an inspection ledger that distinguishes completed, skipped, failed, and excluded
  analysis.

The documentation also states that:

- scanned skills are not executed;
- LLM analysis sends file contents to the configured provider;
- `--no-llm` keeps file contents local;
- the OSV check still sends dependency coordinates to `api.osv.dev`;
- SkillSpector is not a runtime sandbox;
- runtime behavior remains outside static analysis.

## Differentiation erosion

Several capabilities originally considered possible Agent Skill Lab differentiators
are already present in SkillSpector 2.5.0.

| Proposed Agent Skill Lab value | SkillSpector 2.5.0 evidence | Preliminary result |
|---|---|---|
| File and executable inventory | Components and executable metadata in JSON | Strong overlap |
| Capability transparency | LP1-LP4 permission and capability rules | Strong overlap |
| Description-versus-behavior review | TP4 semantic rule | Strong overlap |
| Evidence and remediation | Per-issue location, confidence, explanation, remediation | Strong overlap |
| Stable CI output | JSON, SARIF, documented exit codes | Strong overlap |
| Explicit incomplete checks | 2.5.0 inspection ledger and execution status | Strong overlap |
| False-positive review | Versioned evidence-bound baselines | Strong overlap |
| Scanner integration | CLI, Python API, CI contract, and MCP gate | Strong overlap |
| No execution of inspected skills | Explicit trust boundary | Same baseline |

This means Agent Skill Lab should not be developed as a competing general security
scanner, risk scorer, inventory tool, or generic install gate.

## Finding-level documentary mapping

The table maps the 11 findings in the three completed manual baselines to documented
SkillSpector coverage. It predicts possible overlap; it does not claim that
SkillSpector actually emits a finding until the execution experiment is complete.

| Manual finding | Documentary mapping | Classification |
|---|---|---|
| `ASL-C004-F001` clipboard command dependency | LP3 missing permissions or PE1 excessive permissions may apply | Plausible overlap |
| `ASL-C004-F002` optional repository, GitHub, and CI context | LP1/LP3 and filesystem-enumeration coverage may apply | Plausible overlap |
| `ASL-C005-F001` undeclared Python, Git, TruffleHog, subprocess, and model CLI requirements | LP1/LP3 plus AST4 directly cover much of this | Direct overlap |
| `ASL-C005-F002` external model, authentication, web, and optional credential boundary | E1-E4, PE3, TT3, and TT4 directly cover the security aspect | Direct overlap |
| `ASL-C005-F003` internal symlink portability across installers and Windows | No documented cross-platform packaging or symlink-portability rule found | Candidate gap |
| `ASL-C005-F004` large security-sensitive executable review surface | Executable multiplier and AST rules cover danger, not manual reviewability | Partial overlap |
| `ASL-C005-F005` deliberately fake credential-shaped scanner fixtures | Static rules may alert; LLM context and baselines may resolve it | Experiment required |
| `ASL-C007-F001` strict portable metadata shape versus Hermes nested metadata | No documented versioned Agent Skills/Hermes conformance profile found | Candidate gap |
| `ASL-C007-F002` 500-line progressive-disclosure and on-demand reference guidance | No documented authoring-quality or progressive-disclosure rule found | Candidate gap |
| `ASL-C007-F003` undeclared environment, network, tools, installation, and authentication assumptions | LP1/LP3 and multiple security categories directly overlap | Direct overlap |
| `ASL-C007-F004` package installation, credential entry, service persistence, and sudo | SC, PE2, PE3, and RA2 directly overlap | Direct overlap |

Documentary totals:

- direct overlap: 4;
- plausible or partial overlap: 4;
- candidate compatibility gap: 3.

## Remaining defensible scope

The documentary comparison found no pinned SkillSpector documentation for:

1. strict Agent Skills specification conformance with versioned normative sources;
2. separate OpenClaw and Hermes discovery, metadata, packaging, and capability
   profiles;
3. cross-platform resource and symlink portability;
4. authoring-quality checks such as progressive disclosure;
5. a compatibility matrix that preserves each platform layer rather than reducing
   the result to one install recommendation.

Repository code searches for `OpenClaw`, `Hermes`, `metadata.openclaw`, and
`metadata.hermes` returned no indexed result at the pinned commit. Search absence is
not proof of missing runtime behavior, so these remain hypotheses for the execution
experiment.

## Preliminary product verdict

The broad Agent Skill Lab vision is not currently justified as a standalone competing
scanner. NVIDIA has substantial implementation, distribution, CI, registry, and
governance advantages, and several planned differentiators already overlap with
SkillSpector.

A narrower project may still be justified:

> A deterministic, vendor-neutral compatibility linter for the Agent Skills core,
> OpenClaw, and Hermes that composes SkillSpector rather than replacing it.

This narrower direction is suitable as an open-source research and portfolio project.
The documentary evidence does not yet support treating it as a likely source of
near-term revenue.

## Execution gate

Run one pinned SkillSpector 2.5.0 static-only comparison against:

- `ASL-C004` (`handoff`);
- `ASL-C005` (`autoreview`);
- `ASL-C007` (`llm-wiki`).

The experiment must:

- use the exact pinned SkillSpector and corpus commits;
- use an ephemeral, uncredentialed environment;
- mount or copy samples read-only;
- run with `--no-llm`;
- disable container network access so OSV uses its offline fallback;
- execute no corpus script, hook, test, or command;
- retain raw JSON output and hashes;
- record scanner exit status and completeness fields;
- compare scanner findings with the 11 manual findings without treating either source
  as automatically correct.

## Go or stop criteria

Continue only if the experiment confirms at least three actionable compatibility
findings that:

- SkillSpector does not report;
- cover at least two different rule families;
- occur across at least two of the three samples;
- have clear user-facing impact and deterministic remediation.

If the criteria fail:

- stop the remaining nine manual baselines;
- preserve the repository as a completed research artifact;
- consider contributing missing compatibility checks upstream;
- move primary product exploration to another problem.
