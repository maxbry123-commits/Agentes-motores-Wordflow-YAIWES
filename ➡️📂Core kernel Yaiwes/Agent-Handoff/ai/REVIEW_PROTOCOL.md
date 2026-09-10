---
type: review_protocol
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Actionable Review Handoff Protocol

This file defines how a reviewer hands correction work to an implementation agent and how the agent returns it for verification.

GitHub Pull Request reviews and review threads remain the source of work truth. Do not duplicate full discussions in `ai/`.

## Finding classes

Every review finding that may affect merge readiness must be classified explicitly:

- `blocking` - must be corrected, withdrawn, or explicitly accepted by an authorized maintainer before merge;
- `non-blocking` - recommendation or follow-up that does not prevent merge;
- `question` - request for clarification that is not implicitly blocking.

An ambiguous comment is not a blocking finding until the reviewer marks it as blocking and provides the required correction contract.

Security and evidence findings remain subject to the proportionality rule in `AGENT_HANDOFF_STANDARD.md`. This protocol defines how an eligible blocker is handed off; it does not make an ineligible finding blocking.

When the platform supports pending reviews, the reviewer SHOULD batch findings and submit the completed review before an agent begins correction work.

## Blocking correction contract

A blocking review MUST provide enough information for another agent to correct and verify the defect without relying on private chat history.

Each blocking finding must include:

1. `Finding ID` - a stable identifier unique within the Pull Request, such as `RH-01`;
2. `Evidence and reproduction` - the relevant location, trigger, event order when material, observed result, and expected result; when runtime reproduction is not applicable, cite the exact acceptance criterion or verified mandatory requirement;
3. `Violated contract` - the behavioral, architectural, compatibility, security, or acceptance contract that is not satisfied;
4. `Cause` - `confirmed`, `likely`, or `unknown`, followed by the established cause or bounded hypothesis;
5. `Required outcome` - the observable state that must become true;
6. `Invariants and scope guard` - behavior and controls that must remain true, plus material non-goals or areas that must not be changed;
7. `Verification` - the minimum applicable regression, negative, security, concurrency, or other checks and the evidence expected from them;
8. `Acceptance criteria` - observable conditions for reviewer verification.

`Implementation guidance` is optional. When present, it should identify a recommended approach and any constraints on acceptable alternatives.

Do not claim a root cause is confirmed when it is only inferred. Do not require positive, negative, security, and race tests mechanically for every finding. Select the checks that can fail under the identified scenario; race tests are required only when concurrency, lifecycle ordering, cancellation, retries, cleanup, or shared state is relevant.

One correction contract may cover multiple locations only when they share the same violated contract, required outcome, invariants, and verification. Otherwise use separate finding IDs.

## Implementation freedom and scope

The required outcome, invariants, applicable mandatory requirements, and acceptance criteria are normative.

Implementation guidance is not a hidden acceptance criterion. An agent may use an equivalent approach when it satisfies the required outcome, preserves the stated invariants, remains inside the execution envelope, and provides the required evidence. The agent must explain a material deviation from the recommendation.

A reviewer MUST NOT reject an equivalent correction solely because it does not follow optional implementation guidance.

A review finding does not widen the agent's authority or the original Issue scope. If every safe correction requires an architecture, baseline, permission, destructive-action, external-effect, resource, or other out-of-envelope change, the agent must stop, explain the minimum required expansion, and request the applicable owner decision.

## Blocking finding template

```md
### RH-01 - <short title>

Disposition: blocking

Evidence and reproduction:
- <location, trigger, event order when material, observed result, expected result>

Violated contract:
- <behavioral, architectural, compatibility, security, or acceptance contract>

Cause:
- Status: confirmed | likely | unknown
- <cause or bounded hypothesis>

Required outcome:
- <observable state that must become true>

Invariants and scope guard:
- <behavior or control that must remain true>
- <material non-goal or area that must not change>

Implementation guidance:
- Recommended: <approach, or none>
- Acceptable alternatives: <constraints, or any equivalent outcome-preserving approach>

Verification:
- <minimum applicable checks and expected evidence>

Acceptance criteria:
- <observable conditions for re-review>
```

## Agent correction report

After addressing a review, the implementation agent writes one compact correction report in the Pull Request. It maps every blocking finding ID to the correction and evidence.

Use the template in `ai/TASK_REPORT_PROTOCOL.md`.

The agent may mark a finding `addressed`, `disputed`, `blocked`, or `not-addressed`.

- `addressed` means the agent believes the correction contract is satisfied;
- `disputed` means the agent provides evidence that the finding, violated contract, or required outcome is incorrect or inapplicable;
- `blocked` means a verified boundary prevents a safe in-envelope correction;
- `not-addressed` means the finding remains open.

`addressed` does not mean `verified` and does not automatically resolve a review thread.

## Verification lifecycle

Finding state is distinct from Pull Request state:

```text
open -> addressed -> verified
```

Only the reviewer or another authorized maintainer marks a blocking finding `verified`. Failed verification reopens the finding with updated evidence.

`disputed`, `blocked`, and `not-addressed` remain open until the reviewer withdraws the finding, an authorized owner accepts the relevant outcome or risk, or a correction is addressed and verified.

The normal Pull Request label transition is:

```text
in-review -> changes-requested -> in-review -> ready-to-merge
```

Return the Pull Request to `in-review` after the correction report and required checks are available. Move it to `ready-to-merge` only after every blocking finding is verified or otherwise validly dispositioned and required checks pass.

## Proportionality

The complete correction contract is mandatory only for blocking findings.

Non-blocking findings and questions may remain concise, but must be clearly classified. Optional suggestions belong in follow-up work when they would expand the current scope or delay the primary outcome.

This protocol does not require automated semantic scoring of review quality, a repository file for every review, or a new Issue for every correction cycle.
