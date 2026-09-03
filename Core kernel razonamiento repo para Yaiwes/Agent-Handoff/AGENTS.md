# Repository Guide

Before meaningful work, read these files:

1. `AGENTS.md`
2. `AGENT_HANDOFF_STANDARD.md`
3. `ai/README.md`
4. `ai/GITHUB_WORKFLOW.md`
5. `ai/HANDOFF_PROTOCOL.md`
6. `ai/AGENT_IDENTITY.md`
7. `ai/WORK_CLAIM_PROTOCOL.md`
8. `ai/TASK_REPORT_PROTOCOL.md`
9. `ai/PROJECT_STATE.md`
10. `ai/DECISIONS.md`
11. `ai/CONTAINERIZATION.md` when Docker or Compose is used, planned, present, or being discussed
12. related Issue or PR
13. relevant handoffs through `ai/handoffs/INDEX.md`

Use GitHub Issues and Pull Requests as the primary workflow system.

Report each meaningful Issue with a required stage or final result comment.

For Pull Request review or `changes-requested` work, read `ai/REVIEW_PROTOCOL.md`. A blocking finding must provide a sufficient correction contract, while implementation guidance remains non-binding unless an exact mandatory requirement is cited. An agent-reported `addressed` finding still requires reviewer verification.

Prioritize the stated primary outcome and its smallest acceptance proof. Record the execution envelope before implementation. Keep supporting work subordinate: fix localized, reversible supporting-work failures and perform bounded post-fix verification within the same work item and authorization. Create a stage, handoff, or completion target only when the outcome materially advanced, the acceptance proof completed, a verified blocker is outside the execution envelope, or work is genuinely interrupted or transferred. A supporting-tool failure alone does not require new owner approval; request a decision only when an explicit approval boundary is crossed. After two consecutive supporting-only updates without outcome progress, mark the work `progress-stalled` and replan the shortest path.

Security and evidence work MUST NOT block acceptance or expand scope without a verified High or Critical current-scope risk supported by reproducible evidence or a directly applicable authoritative source. A suspected High or Critical risk permits only a short, time-boxed investigation until confirmed. Keep Low, Medium, unrated, and unverified risks non-blocking; preserve the existing security baseline and prioritize the smallest useful end-to-end scenario. An exact acceptance criterion or verified mandatory requirement is an independent blocker only when cited.

When initializing Agent Handoff in a new repository or adding it to an existing repository, ask the user a separate explicit question about containerization and file layout before changing any Docker or Compose structure. Do not infer or automatically select the recommended approach.

Keep `ai/` files compact.
