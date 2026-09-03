---
type: project_state
version: 1
status: active
updated: 2026-07-27
project: Agent_Handoff
---

# Project State

## Current phase

Agent Handoff Standard 1.5.1 is the active standard.

The repository is maintained as an English-only canonical version.

## Implemented

- Landing README and GitHub Pages site.
- English canonical standard document.
- GitHub Issue Forms and Pull Request template.
- Coordinated GitHub Flow.
- Agent identity protocol.
- Work claim protocol.
- Task report protocol for stage and final result comments.
- Actionable review handoff protocol for blocking correction contracts and reviewer verification.
- Refactoring workflow.
- FAQ and examples.
- GitHub Actions checks workflow.
- Citation metadata.
- GUI testing rule against position-dependent automated tests.
- Containerization protocol with explicit user-controlled layout selection.
- Mandatory separate containerization question for new-repository initialization and existing-repository adoption.
- Supported no-containerization, colocated, centralized, hybrid, modular monorepo, separate deployment repository, and preserved custom layouts.
- Container migration, Compose path, verification, project-memory, and handoff requirements.
- Security and evidence may block or expand scope only for verified High or Critical current-scope risks or exactly cited mandatory requirements.
- Suspected High or Critical risks permit only short, time-boxed investigation until confirmed.
- Low, Medium, unrated, and unverified risks remain non-blocking.
- Early smallest useful end-to-end scenario for MVPs, prototypes, and runtime spikes.
- Non-binding 10–15% security-and-evidence planning heuristic.
- Required primary outcome, smallest acceptance proof, and execution envelope for meaningful work.
- Supporting work remains minimum sufficient and subordinate to the primary outcome.
- Localized reversible supporting-work fixes and bounded post-fix verification remain inside the current authorization and execution envelope.
- Outcome-based stage and handoff boundaries.
- `progress-stalled` recovery after two consecutive supporting-only updates without outcome progress.
- Structural checks for the outcome fields without automated semantic progress scoring.
- Stable review finding IDs with cause confidence, required outcomes, invariants, scope guards, applicable verification, and acceptance criteria.
- Agent correction reports that keep `addressed` distinct from reviewer-confirmed `verified`.
- Implementation freedom for equivalent safe corrections that satisfy the correction contract.

## Main files

- `AGENT_HANDOFF_STANDARD.md`
- `AGENTS.md`
- `ai/README.md`
- `ai/GITHUB_WORKFLOW.md`
- `ai/HANDOFF_PROTOCOL.md`
- `ai/AGENT_IDENTITY.md`
- `ai/WORK_CLAIM_PROTOCOL.md`
- `ai/TASK_REPORT_PROTOCOL.md`
- `ai/REVIEW_PROTOCOL.md`
- `ai/REFACTORING.md`
- `ai/CONTAINERIZATION.md`
- `.github/pull_request_template.md`
- `scripts/check_agent_handoff.py`
- `docs/releases/v1.5.1.md`

## Active decisions

- Container layout is selected by the user, not inferred by an agent.
- The hybrid layout may be recommended but cannot be selected automatically.
- Existing container infrastructure cannot be migrated without explicit approval.
- Position-dependent GUI tests stay outside the routine automated test suite.
- Automated GUI tests use stable semantic selectors.
- Blocking or scope-expanding security and evidence work requires a verified High or Critical current-scope risk or an exactly cited mandatory requirement.
- Existing security baselines stay intact unless the owner explicitly approves a change.
- Low, Medium, unrated, unverified, and otherwise unsupported hardening remains non-blocking and does not delay the smallest useful vertical slice.
- Meaningful work records a primary outcome, smallest acceptance proof, and execution envelope before implementation.
- The execution envelope records existing authorization and cannot be used by an agent to widen its own authority.
- Supporting-tool failures do not create separate stages, handoffs, completion targets, or approval gates unless an explicit outcome or approval boundary is crossed.
- One bounded post-fix verification rerun is permitted after each relevant fix unless the execution envelope is stricter.
- Two consecutive supporting-only updates without outcome progress trigger `progress-stalled` and shortest-path replanning.
- Blocking review findings require a sufficient correction contract; non-blocking findings and questions remain lightweight.
- Implementation guidance does not become a hidden acceptance criterion when an equivalent safe correction satisfies the required outcome and invariants.
- Agent-reported `addressed` findings remain open until reviewer or authorized maintainer verification.

## Current publication

- Standard version: `1.5.1`
- Status: active
- Publication date: 2026-07-27
- Issue: #18
- Pull Request: #19

## Next

1. Keep repository checks and public documentation synchronized with future standard changes.
2. Collect feedback from projects adopting outcome-oriented execution and actionable review handoffs.
3. Prepare a future version only through a focused Issue, branch, Pull Request, checks, and release handoff.
