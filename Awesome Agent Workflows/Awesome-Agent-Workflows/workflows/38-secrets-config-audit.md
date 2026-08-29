# Secrets and Config Audit

## Trigger

Before public release, CI setup, deployment, or repository handoff.

## Goal

Find exposed secrets, unsafe defaults, config drift, and docs that request secrets insecurely.

## Agent brief

```text
You are executing the "Secrets and Config Audit" workflow.

Context:
- Repo/system: [name and path]
- User goal: [goal]
- Current state: [branch, issue, incident, test failure, or source material]
- Allowed scope: [files, commands, services]
- Forbidden scope: [secrets, production, unrelated files, destructive actions]

Required output:
- Scope summary
- Actions taken
- Evidence collected
- Files changed
- Verification commands and results
- Open risks and decisions needed
```

## Steps

1. **Restate the contract.** Say what will be changed, what will not be changed, and what evidence is required.
2. **Collect targeted context.** Read only the files, logs, docs, issues, or commands needed for this workflow.
3. **List assumptions.** Mark each assumption as verified, unverified, or requiring human input.
4. **Execute the smallest safe increment.** Prefer a small patch, checklist, doc update, or diagnostic over broad rewrites.
5. **Record evidence inline.** Keep command names, exit codes, links, screenshots, or source paths with every claim.
6. **Run workflow-specific verification.** Use the checklist below before reporting success.
7. **Leave a handoff.** Include next actions, stop conditions, and what should not be trusted without re-checking.

## Verification checklist

- [ ] Scope boundaries and non-goals are explicit.
- [ ] Every factual claim has evidence from a file, command, log, screenshot, issue, PR, or cited source.
- [ ] Verification commands or observable checks are listed with results.
- [ ] Human approval gates below were respected.
- [ ] No secrets, credentials, private customer data, or unauthorized production actions are exposed.

## Failure modes

- The agent broadens scope because it notices adjacent cleanup.
- The agent treats a generated summary as evidence.
- The agent reports success before running the final check.
- The agent hides uncertainty instead of labeling unverified assumptions.
- The agent changes public, production, or destructive state without approval.

## Human gate

Human rotates/revokes real secrets and approves config changes.

## Good output example

```text
Summary: [one-paragraph result]
Evidence: [commands, files, links]
Changed: [files or none]
Verification: [exact checks and results]
Risks: [remaining uncertainty]
Next: [safe next step]
```
