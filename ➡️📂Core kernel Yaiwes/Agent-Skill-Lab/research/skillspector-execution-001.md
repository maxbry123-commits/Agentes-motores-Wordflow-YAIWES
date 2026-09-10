# SkillSpector Differentiation Execution 001

**Status:** completed
**Run date:** 2026-07-30
**Decision:** narrow offline compatibility thesis passes the provisional gate

## Execution identity

- Workflow run:
  [30513305712](https://github.com/ricardoml96/agent-skill-lab/actions/runs/30513305712)
- Job: `static-comparison` (`90777737640`)
- Workflow conclusion: `success`
- Runner: GitHub-hosted Ubuntu 24.04
- SkillSpector version: `2.5.0`
- SkillSpector commit: `34f60308522f45447cd343da0aad77bcea308ad4`
- OpenClaw corpus commit: `fe588b1a6267eb47f785d0c748db9f6f3e9a3b4f`
- Hermes corpus commit: `202140db53536083b85aba7511c555d07f5ada67`

## Safety controls confirmed

The run:

- used an ephemeral GitHub-hosted runner;
- granted the workflow read-only repository contents permission;
- used immutable source commits;
- ran SkillSpector with `--no-llm`;
- disabled network access inside each scan container;
- mounted corpus sources read-only;
- used a read-only container root, dropped all capabilities, enabled
  `no-new-privileges`, and limited processes, memory, and CPU;
- did not execute corpus scripts, hooks, tests, installers, or commands.

The Docker image build required network access to obtain its pinned base image and
declared package dependencies. The scans themselves had no network access.

## Scanner result summary

| Sample | Exit | Risk result | Issues | JSON SHA-256 |
|---|---:|---|---:|---|
| `ASL-C004` / `handoff` | 0 | 0, LOW, SAFE | 0 | `4fd3d54a87313f0b827629d994b75dfcfbb0b33d621839fd21b8366ac8a93545` |
| `ASL-C005` / `autoreview` | 1 | 100, CRITICAL, DO_NOT_INSTALL | 156 | `795b6825c1e6f1d1de097aed524c0303922de74eda84b34525d98a33ed1e1f06` |
| `ASL-C007` / `llm-wiki` | 0 | 6, LOW, SAFE | 1 | `3db5aa26c25d08c1e5c06d8d212ad515eff01b6e342b313f825e8fbdeebf88cf` |

Exit code 1 for `ASL-C005` is the scanner's expected policy result for significant
findings. The JSON report still records `execution_successful: true`.

All three reports recorded 100% component coverage. They also recorded
`is_complete: false` because semantic and LLM-backed analyzers were deliberately
disabled. The result is therefore an offline static comparison, not a claim about
every optional SkillSpector mode.

## Manual finding comparison

| Manual finding | Execution result | Gate treatment |
|---|---|---|
| `ASL-C004-F001` clipboard runtime dependency | SkillSpector emitted no issue | Confirmed offline gap |
| `ASL-C004-F002` repository, GitHub, and CI context requirements | SkillSpector emitted no issue | Confirmed offline gap |
| `ASL-C005-F001` undeclared runtime prerequisites | LP3 and AST4 materially overlap | Overlap |
| `ASL-C005-F002` external data and credential boundary | E1, E2, PE3, and related findings materially overlap | Overlap |
| `ASL-C005-F003` symlink portability | The link was flattened into a Markdown component with no portability issue | Confirmed offline gap |
| `ASL-C005-F004` large executable review surface | Line counts were inventoried, but no reviewability finding was emitted | Additional quality gap; not needed for gate |
| `ASL-C005-F005` synthetic secret fixture context | No issue was emitted for the fixture | Research observation; not counted |
| `ASL-C007-F001` portable metadata shape | No conformance issue was emitted | Confirmed offline gap |
| `ASL-C007-F002` progressive disclosure | The 507-line document was inventoried, but no quality issue was emitted | Confirmed offline gap |
| `ASL-C007-F003` undeclared runtime assumptions | No relevant permission or prerequisite issue was emitted | Confirmed offline gap |
| `ASL-C007-F004` privileged or persistent optional setup | RA2 alerted on unrelated archive/log wording and missed the actual setup section | Additional security-context gap; not needed for gate |

The conservative gate count is six actionable offline gaps:

1. clipboard runtime availability;
2. external repository and CI context availability;
3. symlink transport portability;
4. portable metadata conformance;
5. progressive-disclosure quality;
6. undeclared runtime assumptions.

They occur across all three samples and cover at least four rule families:
capability availability, transport portability, metadata conformance, and authoring
quality. This exceeds the required three findings across two samples and two rule
families.

## Interpretation

The result supports only this narrower direction:

> A deterministic, vendor-neutral compatibility linter for the Agent Skills core,
> OpenClaw, and Hermes that can compose SkillSpector for security analysis.

It does not support building:

- another general security scanner;
- a competing risk score;
- a replacement for SkillSpector;
- a product whose value depends only on detecting suspicious code.

The `ASL-C005` result also shows why scanner output needs context. A large defensive
test corpus generated 156 issues and a critical verdict. That may be policy-correct
for an installation gate, but it does not by itself prove malicious intent.

## Product decision

The technical differentiation gate passes provisionally for offline deterministic
compatibility. Commercial demand and willingness to pay remain untested.

Before implementing a substantial product:

1. reduce the concept to a small compatibility-only rule set;
2. validate the rules on a few additional deliberately selected packages;
3. present the output to real skill authors or maintainers;
4. stop if the findings do not change an authoring, review, or installation decision.

The remaining nine broad manual baselines should not resume unchanged. Any further
corpus work should be targeted at the confirmed compatibility rule families.
