# Workflow Catalog
This catalog helps you choose the right workflow before handing real work to an AI agent.
## Choose by situation
- Fuzzy feature: `01` then `12`.
- Parallel work: `02` and `35`.
- Bug fix: `13`, `14`, then `03`.
- CI failure: `19`.
- Flaky tests: `20`.
- Merge review: `16` then `04`.
- Security/public release: `05`, `38`, then `07`.
- Long-running or interrupted work: `40` and `36`.
- Prompt, policy, or memory changes: `31` and `32`.
## Workflows by category
### Planning
- [`01` Spec → Plan → Implementation](../workflows/01-spec-to-plan.md) — The request is vague or multi-step.
- [`11` Change Impact Map](../workflows/11-change-impact-map.md) — Before an agent edits unfamiliar code or a risky area.
- [`12` Agent Task Contract and Scope Box](../workflows/12-agent-task-contract.md) — Before delegating a task to an AI agent.

### Execution
- [`02` Parallel Agent Development](../workflows/02-parallel-agent-development.md) — Multiple independent tasks can run at once.
- [`35` Git Worktree Agent Lanes](../workflows/35-git-worktree-agent-lanes.md) — Multiple agents or humans need to work in the same repo concurrently.
- [`36` Context Compaction and Handoff](../workflows/36-context-compaction-handoff.md) — A long agent session is about to compact, hand off, or restart.
- [`40` Long-Running Task Checkpoint](../workflows/40-long-running-task-checkpoint.md) — A build, migration, scrape, benchmark, agent run, or batch job will run for a while.

### Implementation
- [`18` API Contract Change Lockstep](../workflows/18-api-contract-lockstep.md) — Changing public APIs, schemas, events, CLI flags, or config formats.
- [`34` Multi-Repo Change Coordinator](../workflows/34-multi-repo-change-coordinator.md) — A change spans multiple repositories, packages, services, docs, or deployment units.

### Debugging
- [`03` Root-Cause Debugging](../workflows/03-bug-root-cause.md) — A bug is unclear or recurring.
- [`13` Regression-Test-First Bug Fix](../workflows/13-regression-test-first-bugfix.md) — A bug has a concrete symptom or user report.
- [`14` Minimized Reproducer Factory](../workflows/14-minimized-reproducer-factory.md) — A bug is vague, flaky, environment-specific, or reported only in logs.

### Testing
- [`20` Flaky Test Burn-Down](../workflows/20-flaky-test-burndown.md) — A test passes on rerun but fails intermittently.

### CI
- [`19` CI Red-to-Green Reproducer](../workflows/19-ci-red-to-green.md) — CI fails after an agent change.

### Review
- [`04` Fresh-Context Code Review](../workflows/04-fresh-context-code-review.md) — Before merging or trusting agent-authored code.
- [`16` Agent Patch Intake Triage](../workflows/16-patch-intake-triage.md) — An agent returns a diff, branch, patch, or pull request.
- [`17` Review Feedback Application Loop](../workflows/17-review-feedback-loop.md) — A reviewer left comments on an agent-authored PR.

### Refactoring
- [`15` Golden Master Refactor](../workflows/15-golden-master-refactor.md) — Refactoring legacy or under-tested code where behavior must stay stable.

### Security
- [`05` Security Review Sprint](../workflows/05-security-review.md) — Code touches auth, secrets, network, parsers, permissions, or public release.
- [`38` Secrets and Config Audit](../workflows/38-secrets-config-audit.md) — Before public release, CI setup, deployment, or repository handoff.

### Safety
- [`32` Agent Memory Hygiene Review](../workflows/32-agent-memory-hygiene-review.md) — Memory feels wrong, stale, conflicting, too full, or privacy-sensitive.
- [`37` MCP and Tool Integration Review](../workflows/37-mcp-tool-integration-review.md) — Adding or changing an MCP server, tool, plugin, or external integration.

### Release
- [`07` Release Runbook](../workflows/07-release-runbook.md) — A change is ready to publish, deploy, or announce.
- [`22` Urgent Hotfix Fast Path](../workflows/22-urgent-hotfix-fast-path.md) — A production-impacting regression needs a fast patch.
- [`25` Migration Readiness and Cutover Planner](../workflows/25-migration-cutover-planner.md) — A schema, API, platform, vendor, or data migration is proposed.

### Operations
- [`23` Incident Command Center](../workflows/23-incident-command-center.md) — A pager alert, customer-impacting incident, or severe degradation is active.
- [`24` Blameless Postmortem and Action Ledger](../workflows/24-blameless-postmortem-ledger.md) — An incident is stabilized or closed.

### Documentation
- [`26` Documentation Drift Audit](../workflows/26-documentation-drift-audit.md) — Docs may be stale after feature, process, or dependency changes.
- [`27` ADR Decision Capture from Threads](../workflows/27-adr-decision-capture.md) — A decision happened in chat, meeting notes, issue comments, or PR discussion.
- [`39` Agent-Written Docs Review](../workflows/39-agent-written-docs-review.md) — An agent produced README, API docs, changelog, tutorial, or launch copy.

### Team
- [`28` Role-Based Onboarding Trail](../workflows/28-role-based-onboarding-trail.md) — A new hire, transfer, contractor, or agent needs to ramp into a repo or system.
- [`29` Knowledge Transfer and Bus-Factor Reduction](../workflows/29-bus-factor-reduction.md) — A system depends on one person, a rotation is coming, or ownership is changing.

### Evaluation
- [`30` Workflow Evaluation Harness](../workflows/30-workflow-evaluation-harness.md) — A new agent workflow, prompt, or automation needs repeatable quality checks.
- [`31` Prompt and Policy Change Control](../workflows/31-prompt-policy-change-control.md) — Changing system prompts, guardrails, tool permissions, routing, or memory policy.

### Product
- [`33` Customer Signal to Roadmap Triage](../workflows/33-customer-signal-roadmap-triage.md) — Support tickets, interviews, reviews, sales notes, or churn reasons accumulate.

### Research
- [`08` Research Brief](../workflows/08-research-brief.md) — A decision depends on current facts or external sources.

### Infrastructure
- [`09` Local AI Stack Setup](../workflows/09-local-ai-stack.md) — A local or self-hosted AI stack is needed.

### Maintenance
- [`21` Dependency Upgrade Shepherd](../workflows/21-dependency-upgrade-shepherd.md) — Bumping libraries, frameworks, runtimes, lockfiles, or build tools.

### Growth
- [`10` Repo Growth Launch](../workflows/10-repo-growth-launch.md) — A public repository needs useful packaging and launch readiness.

### QA
- [`06` Browser Runtime QA](../workflows/06-browser-qa.md) — A browser app, page, or automation flow needs validation.

## Risk levels

- **Low**: documentation, research, or process work with no production side effects.
- **Medium**: code, test, CI, or workflow changes that can break local or repository state.
- **High**: auth, secrets, production, migrations, public release, tool permissions, memory, or incident response.

## Machine-readable index

The same catalog is available as [`agent-workflows.json`](../agent-workflows.json) with trigger, risk level, tags, and verification fields.
