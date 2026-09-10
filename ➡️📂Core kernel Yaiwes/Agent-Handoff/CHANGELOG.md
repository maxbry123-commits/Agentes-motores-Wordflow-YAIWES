# Changelog

All notable changes to Agent Handoff are documented here.

## 1.5.1 - 2026-07-27

### Why

- Standard 1.5 defined when work and findings may block progress, but it did not define how a reviewer hands a blocking finding back to an implementation agent. A bare defect statement could cause clarification loops, accidental scope expansion, weakened invariants, or treatment of an implementation suggestion as a hidden acceptance criterion.

### Added

- `ai/REVIEW_PROTOCOL.md` with blocking, non-blocking, and question classifications.
- A required blocking correction contract with stable finding ID, evidence, violated contract, cause confidence, required outcome, invariants, scope guard, applicable verification, and acceptance criteria.
- Agent Handoff Review Correction Report mapped by finding ID.
- Finding lifecycle `open -> addressed -> verified`, distinct from Pull Request labels.
- Release notes in `docs/releases/v1.5.1.md`.

### Changed

- Implementation guidance is explicitly non-binding when an equivalent safe correction satisfies the required outcome, preserves invariants, remains inside the execution envelope, and provides the required evidence.
- Root-cause confidence must be marked `confirmed`, `likely`, or `unknown`.
- Positive, negative, security, and race tests are selected by applicability rather than required mechanically for every finding.
- Agent-reported `addressed` status no longer implies reviewer verification or automatic review-thread resolution.
- GitHub workflow, task reporting, handoff rules, Pull Request checklist, public documentation, and structural checks now cover the correction loop.

## 1.5 - 2026-07-26

### Why

- Standard 1.4 constrained disproportionate security and evidence work, but the general workflow still allowed a failed smoke wrapper, test harness, CI layer, evidence collector, or other supporting tool to become its own stable stage, handoff, approval gate, and completion target. This could create repeated process loops without advancing the Issue's primary outcome.

### Added

- Required `Primary outcome`, `Smallest acceptance proof`, and `Execution envelope` fields for meaningful work claims.
- Normative distinction between an unchanged retry and bounded post-fix verification.
- Explicit authorization and approval boundaries for localized supporting-work fixes.
- Outcome-based stage and handoff boundaries.
- A `progress-stalled` rule after two consecutive supporting-only updates without outcome progress.
- Release notes in `docs/releases/v1.5.md`.

### Changed

- Supporting work must remain minimum sufficient and cannot become an independent stage, handoff, approval gate, or completion target merely because it failed or required repair.
- Task reports now record outcome progress, acceptance proof, supporting work, verified blockers, and the next direct outcome step.
- Stage results now require material outcome progress, completed acceptance proof, a verified out-of-envelope blocker, or genuine interruption or transfer.
- The original authorization now explicitly covers reversible in-scope implementation, localized blocker fixes, focused tests, and bounded verification reruns inside the declared execution envelope.
- The execution envelope records existing authorization and cannot be used by an agent to create or widen its own authority.
- The Pull Request checklist and structural checker verify the new protocol fields without attempting to judge semantic progress automatically.

## 1.4 - 2026-07-24

### Added

- Normative proportional-security and evidence rule for blocking work and scope expansion.
- Required risk classification for blocking risk, follow-up hardening, and owner-accepted risk.
- Release notes in `docs/releases/v1.4.md`.

### Changed

- MVPs, prototypes, and runtime spikes now prioritize the smallest useful end-to-end scenario while preserving the existing security baseline and addressing verified High or Critical risks.
- Security work may block acceptance or expand scope only for a verified High or Critical current-scope risk, an exact acceptance criterion, or a verified mandatory requirement.
- Suspected High or Critical risks permit only short, time-boxed investigation until confirmed; Low, Medium, unrated, and unverified risks remain non-blocking.
- The 10–15% security-and-evidence share is explicitly a non-binding planning heuristic, not an acceptance metric or hard cap.
- The Pull Request checklist and structural checker verify the threshold is acknowledged without attempting to score risk automatically.

## 1.3 - 2026-07-18

### Added

- GUI testing rule that prohibits brittle automated tests based on absolute coordinates, screen position, pixel offsets, or incidental layout order.
- `ai/CONTAINERIZATION.md` with supported Docker and Docker Compose organization approaches.
- Supported containerization choices for no repository-managed containers, colocated files, centralized `docker/`, hybrid layout, modular monorepos, separate deployment repositories, and established custom layouts.
- Container layout migration inventory, verification, project-memory, and handoff requirements.
- Release notes in `docs/releases/v1.3.md`.

### Changed

- New-repository initialization and existing-repository adoption now require a separate, explicit user decision about containerization and file layout.
- Agents may not infer, create, relocate, consolidate, or migrate container infrastructure before the user answers the mandatory question.
- The hybrid layout is a recommended option to present, not an automatic default.
- Repository checks and the Pull Request checklist now cover the containerization protocol and decision gate.

## 1.2 - 2026-07-07

### Added

- Coordinated GitHub Flow for humans, autonomous agents, and human-supervised agents.
- Meaningful branch naming without `/`, Issue numbers, or random identifiers by default.
- Agent identity protocol with `agent_name`, `agent_id`, and `run_id`.
- Work Claim protocol with `Coordinator` and `Supervision` fields.
- Mandatory task result reports for large multi-stage Issues and small Issues.
- Refactoring workflow and matching Issue form fields.
- Landing README with problem, solution, use cases, comparison, and search terms.
- GitHub Pages landing site from `/docs`.
- GitHub Actions checks workflow for repository structure and YAML validation.
- `CITATION.cff` metadata.
- Repository discovery settings for About, Website, topics, and social preview.

### Changed

- Repository documentation and templates simplified to English-only canonical files.
- Repository license note finalized as GPL-3.0.
- Repository Website moved from the repository URL to the GitHub Pages site.
- Repository topics aligned with the current public About sidebar.
- Social preview asset updated to use `AI memory` instead of ambiguous `ai/`.

## 1.1 - 2026-06-29

### Added

- Initial Agent Handoff standard structure.
- `ai/` memory map.
- Handoff index.
- Basic Issue and Pull Request templates.
