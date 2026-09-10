# Community Issue Seeds

These issue seeds are designed to make the repo easy to participate in after launch. They should invite concrete contributions without manufacturing fake activity.

Use the labels listed with each seed. Keep the issue bodies factual and update them when feedback turns a seed into real work.

## Seed 1: reviewing agent-generated tests

Title:

Request: workflow for reviewing agent-generated tests

Labels:

- `workflow request`
- `good first issue`

Body:

```markdown
## Requested workflow

A workflow card for reviewing tests written by coding agents.

## Why it matters

Agents often add tests that assert implementation details, mirror the bug, over-mock behavior, or pass without protecting the real user path. A dedicated workflow would help maintainers decide whether agent-generated tests actually catch regressions.

## Useful coverage

- Spotting tests that only verify mocks.
- Checking whether a test fails before the fix.
- Reviewing assertions for behavior rather than implementation details.
- Detecting broad snapshots or brittle fixtures.
- Requiring evidence that the test protects the intended regression.

## Contribution shape

A good contribution would add one workflow card under `workflows/` and update `docs/WORKFLOW-CATALOG.md` and `agent-workflows.json` if needed.
```

## Seed 2: additional tool adapter

Title:

Request: add a tool adapter for another coding agent

Labels:

- `documentation`
- `help wanted`

Body:

```markdown
## Requested adapter

Add a tool adapter for a coding-agent tool that is not covered yet.

Existing adapters include Claude Code, Codex CLI, Cursor, Aider, OpenCode, and local/self-hosted agents.

## Good adapter criteria

- Explains where to paste the agent brief.
- Notes the tool's relevant permissions and file access model.
- Shows how to run verification from the tool or terminal.
- Calls out stop conditions for secrets, destructive actions, production, or repo settings.
- Avoids vendor marketing language.

## Contribution shape

Add a document under `docs/tools/` and link it from the README and any comparison docs if appropriate.
```

## Seed 3: real-world agent failure story

Title:

Good first issue: add a real-world agent failure story and guardrail

Labels:

- `good first issue`
- `documentation`

Body:

```markdown
## Contribution idea

Add a short example of an agent failure mode and the workflow guardrail that would have caught it.

## Good examples

- Agent claimed tests passed but never ran them.
- Agent fixed the symptom but not the root cause.
- Agent changed unrelated files outside scope.
- Agent weakened a failing check instead of fixing the problem.
- Agent used a secret, production endpoint, or unsafe command without approval.

## Expected format

- What the agent was asked to do.
- What went wrong.
- What evidence revealed the issue.
- Which workflow or checklist would have prevented it.
- Any follow-up workflow that should be added.

Please avoid secrets, private customer data, proprietary code, or identifying details from closed-source incidents.
```

## Seed 4: public examples of agent runbooks

Title:

Resource suggestion: collect public examples of agent runbooks and operating contracts

Labels:

- `resource suggestion`
- `help wanted`

Body:

```markdown
## Resource request

Collect high-quality public resources that show practical operating contracts for coding agents: task briefs, review workflows, CI loops, tool permission policies, handoff formats, or release runbooks.

## Include

- Public links with durable URLs.
- A short explanation of why the resource is useful.
- Notes about which workflow it complements.

## Exclude

- Prompt dumps without verification or scope boundaries.
- Vendor marketing pages with no operational detail.
- Referral links, paid placements, or spam.
- Anything that asks users to paste secrets into prompts.
```

## Seed 5: worked example for parallel agent lanes

Title:

Request: worked example for parallel agent worktree lanes

Labels:

- `workflow request`
- `documentation`

Body:

```markdown
## Requested example

Add a worked example showing how to split one feature or cleanup across multiple coding-agent lanes using git worktrees.

## Why it matters

Parallel agents can create duplicate work, branch conflicts, and unverified integration. A concrete example would make the parallel-agent and worktree-lane workflows easier to apply.

## Useful coverage

- How the task is split into independent lanes.
- Branch/worktree naming.
- Per-lane scope boundaries.
- Integration order.
- Verification before merge.
- What to do when two agents touch the same file.

## Contribution shape

Add an example under `examples/` and link it from the relevant workflow cards.
```
