---
type: architecture_record
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Architecture Records

## 2026-06-29 — Adopt Agent Handoff Standard 1.1

Status: accepted

### Background

The initial standard needed support for parallel agents, GitHub templates, smoke tests, and machine-readable metadata.

### Decision

Adopt Agent Handoff Standard 1.1 as a compact workflow scaffold.

### Related

- Issue: #1

## 2026-07-02 — Rename to Agent Handoff

Status: accepted

### Background

The project name should emphasize agent-to-agent development handoff.

### Decision

Use Agent Handoff as the project and standard name.

### Related

- Standard file: `AGENT_HANDOFF_STANDARD.md`

## 2026-07-07 — English-only canonical repository

Status: accepted

### Background

The public repository should be simpler to maintain and easier for an international audience to scan.

### Decision

Maintain this repository in English only. Downstream projects may adapt Agent Handoff to another repository language, but canonical files here stay English-only.

### Related

- `AGENT_HANDOFF_STANDARD.md`
- `docs/en/README.md`

## 2026-07-18 — User-controlled containerization layout

Status: accepted in Standard 1.3

### Background

Docker and Docker Compose files can be organized in several valid ways. Automatically applying one preferred structure during repository initialization or Agent Handoff adoption could create unnecessary migrations, break paths and commands, or override established project ownership boundaries.

### Decision

Document all supported containerization approaches in `ai/CONTAINERIZATION.md`.

During both new-repository initialization and adoption into an existing repository, require the agent to ask the user a separate, explicit question about whether containerization is used or planned, which layout should be used, whether an existing layout may be migrated, and whether production deployment belongs in the same repository.

Do not allow the agent to infer approval or automatically apply the recommended hybrid layout.

### Rejected alternatives

- Require one universal Docker layout for all repositories.
- Automatically migrate existing repositories to the hybrid layout.
- Treat the container layout as an implementation detail that the agent may decide silently.
- Create placeholder Docker infrastructure before a confirmed requirement exists.

### Consequences

- Container layout remains a human-controlled architecture decision.
- Existing repositories are preserved until migration is explicitly approved.
- New repositories do not receive speculative Docker infrastructure.
- Agents have a complete catalog of supported layouts and shared verification requirements.
- Initialization prompts and handoff procedures expose the decision gate explicitly.

### Related

- Issue: #12
- Pull Request: #13
- `AGENT_HANDOFF_STANDARD.md`
- `ai/CONTAINERIZATION.md`
- `ai/HANDOFF_PROTOCOL.md`

- `docs/en/README.md`

## 2026-07-18 — Stable GUI automation over position-dependent tests

Status: accepted in Standard 1.3

### Background

GUI tests that depend on absolute coordinates, screen positions, pixel offsets, or incidental layout order are fragile and frequently fail after harmless interface changes.

### Decision

Do not include position-dependent GUI checks in the routine automated test suite. Perform those checks manually or as supervised exploratory checks with Codex.

Automated GUI tests use stable semantic roles, accessible names, labels, documented component identifiers, or dedicated test IDs.

### Consequences

- Routine GUI automation is more resilient to layout changes.
- Visual and position-dependent behavior remains explicitly testable through manual or supervised exploratory checks.
- Handoffs and Pull Requests must state when such checks were performed manually.

### Related

- Issue: #12
- Pull Request: #13
- `AGENT_HANDOFF_STANDARD.md`

## 2026-07-24 — Proportionate security and evidence

Status: accepted in Standard 1.4

### Background

The standard required risks and checks to be recorded but did not require security and evidence work to be proportional to a risk in the current scope. Hypothetical threats could therefore create blocking gates, extra documents, or separate stages before a useful end-to-end scenario existed.

### Decision

Treat security and evidence work as blocking or scope-expanding only for a verified High or Critical current-scope risk supported by reproducible evidence or a directly applicable authoritative source. Record the scenario, asset or trust boundary, applicability, severity rationale, minimum sufficient control, and smallest verification.

A suspected High or Critical risk permits only a short, time-boxed investigation until confirmed. Low, Medium, unrated, and unverified risks remain non-blocking and belong in warnings, documentation, backlog, explicitly owner-accepted risk, or out of scope.

Preserve the existing security baseline and run the smallest useful vertical slice early. An exact acceptance criterion or verified legal or project requirement may independently block acceptance only when cited.

Use a 10–15% security-and-evidence share only as a non-binding planning heuristic. Substantially exceeding it requires a verified High or Critical risk or an exactly cited mandatory requirement.

### Rejected alternatives

- Require a formal threat model for every Pull Request.
- Enforce a fixed percentage of work for security and evidence.
- Add automated risk-severity scoring.
- Add approval stages or ADRs for theoretical risks.
- Weaken existing controls to accelerate delivery.

### Consequences

- Blocking or scope-expanding security work requires a verified High or Critical current-scope risk or an exactly cited mandatory requirement.
- Suspected High or Critical risks permit only short, time-boxed investigation until confirmed.
- Low, Medium, unrated, and unverified risks remain non-blocking.
- Reviews and handoffs distinguish verified blockers, time-boxed investigations, follow-up hardening, and owner-accepted risk.
- The structural checker confirms the PR checklist item but does not judge evidence or severity.

### Related

- Issue: #14
- Pull Request: #15
- `AGENT_HANDOFF_STANDARD.md`
- `ai/HANDOFF_PROTOCOL.md`
- `ai/TASK_REPORT_PROTOCOL.md`

## 2026-07-26 — Outcome-oriented execution and bounded supporting work

Status: accepted in Standard 1.5

### Background

Standard 1.4 constrained disproportionate security and evidence work, but the general reporting workflow still allowed any repaired supporting layer to qualify as a stable stage. A failure in a test harness, smoke wrapper, CI layer, evidence collector, release helper, or incidental refactoring could therefore create its own report, handoff, owner approval gate, and verification cycle without advancing the Issue's primary outcome.

The missing boundary was general rather than security-specific: the standard did not require an observable primary outcome, a smallest acceptance proof, or an execution envelope, and it did not distinguish an unchanged retry from verification after a relevant fix.

### Decision

Require every meaningful work item to record its primary outcome, smallest acceptance proof, and execution envelope before implementation.

Keep supporting work minimum sufficient. A localized, reversible, in-scope supporting defect and one bounded verification rerun after each evidence-based fix remain inside the current work item and authorization unless the execution envelope is stricter or an explicit approval boundary is crossed.

Treat stage results and handoffs as legitimate only when the primary outcome materially advanced, the acceptance proof completed, a verified blocker remains outside the execution envelope, or work is genuinely interrupted or transferred.

After two consecutive supporting-only updates without outcome progress, require `progress-stalled` recovery: stop optional supporting work, restate the outcome and proof, identify the shortest path, move non-blocking work to follow-up or backlog, and continue or request one owner decision only when a real approval boundary was crossed.

### Approval boundary

A new owner decision remains required for changes to the outcome or acceptance criteria, scope or architecture, accepted baseline, destructive or out-of-envelope external effects, material resource or risk expansion, security-control weakening, and project-specific or platform-enforced permission gates.

### Rejected alternatives

- Extend only the proportional-security rule; the failure mode also applies to non-security supporting work.
- Treat every supporting-tool repair as a separate stage for maximum traceability.
- Require a new approval before every post-fix verification rerun.
- Automatically score semantic outcome progress in the structural checker.
- Use a fixed percentage cap for all supporting work.

### Consequences

- Work claims expose the result, proof, and authorization boundary before implementation.
- Localized supporting failures are repaired and verified without unnecessary report-review-approval loops.
- Stage reports and handoffs describe outcome boundaries instead of auxiliary-layer stability.
- `progress-stalled` makes repeated supporting-only checkpoints visible and forces shortest-path replanning.
- Existing safety controls, external permission systems, and explicit project approval gates remain authoritative.
- The structural checker validates required fields but does not attempt to judge whether progress is semantically real.

### Related

- Issue: #16
- Pull Request: #17
- `AGENT_HANDOFF_STANDARD.md`
- `ai/WORK_CLAIM_PROTOCOL.md`
- `ai/TASK_REPORT_PROTOCOL.md`
- `ai/HANDOFF_PROTOCOL.md`

## 2026-07-27 — Actionable review handoff without implementation lock-in

Status: accepted in Standard 1.5.1

### Background

Standard 1.5 defined blocking eligibility, outcome progress, execution envelopes, and approval boundaries, but did not define the reviewer-to-agent correction handoff. A blocking comment could identify a defect without enough reproduction, contract, invariant, verification, or acceptance information for another agent to act independently.

Requiring only a reviewer-proposed implementation would close the information gap by creating a different problem: it could turn guidance into an undocumented acceptance criterion and reject equally safe solutions.

### Decision

Require every blocking finding to carry a stable ID and a sufficient correction contract: evidence or reproduction, violated contract, cause confidence, required outcome, invariants and scope guard, minimum applicable verification, and observable acceptance criteria.

Mark cause confidence as `confirmed`, `likely`, or `unknown`. Treat implementation guidance as optional and non-binding unless an exact mandatory requirement makes the choice normative.

Allow equivalent corrections when they satisfy the required outcome, preserve the stated invariants, remain inside the execution envelope, and provide the required evidence.

Keep finding state distinct from Pull Request state. The implementation agent may mark a finding `addressed`, but only the reviewer or another authorized maintainer marks it `verified`.

Apply the complete contract only to blocking findings. Keep non-blocking findings and questions concise and explicitly classified.

### Rejected alternatives

- Require the full template for every nit, optional suggestion, or question.
- Require every finding to have positive, negative, security, and race tests.
- Treat a reviewer-recommended implementation as the only acceptable correction.
- Let `addressed` automatically resolve a review thread.
- Let a review finding widen the original authorization or Issue scope.
- Add automated semantic scoring of review quality.

### Consequences

- Coding agents receive self-contained, verifiable correction tasks without private chat history.
- Root-cause hypotheses are not represented as confirmed facts.
- Architecture and security invariants remain explicit during correction.
- Review cycles map finding IDs to changes, evidence, and independent verification.
- Equivalent safe implementations remain possible.
- The structural checker validates protocol fields but does not judge review semantics.

### Related

- Issue: #18
- Pull Request: #19
- `AGENT_HANDOFF_STANDARD.md`
- `ai/REVIEW_PROTOCOL.md`
- `ai/TASK_REPORT_PROTOCOL.md`
