# Ethical Growth Plan

Goal: make this repository genuinely useful enough that developers star it because it saves time.

## Non-goals

- No bought stars.
- No star-for-star rings.
- No botting, fake accounts, or deceptive automation.
- No spam comments on unrelated repositories.

## Positioning

One-line pitch:

> Copy-pasteable workflows for shipping real work with AI coding agents safely.

Audience:

- developers using Claude Code, Codex CLI, Cursor, Aider, OpenCode, or local agents;
- maintainers trying to review AI-generated code;
- teams adopting parallel agent workflows;
- people building personal AI operating systems.

## Launch assets to prepare

- README screenshot/social card.
- [Demo GIF](../../assets/demo-workflow.gif) showing a workflow copied into an agent and verified.
- [Launch Pack](LAUNCH-PACK.md) with post-ready copy and reply templates.
- [Posting Checklist](POSTING-CHECKLIST.md) for a staged, feedback-first launch.
- [Community Issue Seeds](COMMUNITY-ISSUE-SEEDS.md) for participation hooks.
- Short launch thread with three concrete examples.
- Show HN post focused on lessons learned, not hype.
- Reddit post for communities that allow project sharing.
- Issue labels for `workflow request`, `resource suggestion`, `good first issue`.

## First 7 days

Day 1:
- publish initial repo;
- verify badges and repo topics;
- add at least 10 workflows;
- ask 5 real agent users for feedback, not stars.

Day 2-3:
- add examples from feedback;
- create comparison matrix for agent tools;
- add a demo GIF.

Day 4-7:
- submit one thoughtful launch post;
- respond to every issue/PR quickly;
- add requested workflows;
- keep README concise and useful.

## Star milestones

- 16 stars: validate the repo page and quick-start are clear.
- 128 stars: add contribution velocity and examples.
- 512 stars: turn popular workflows into reusable templates and maybe a small CLI.
- 4096+ stars: requires breakout usefulness and repeated community sharing.

## Copy bank

### Short post

I made Awesome Agent Workflows: a vendor-neutral library of copy-pasteable operating procedures for coding agents.

Not prompt dumps. Each workflow card includes goal, scope boundaries, verification gates, stop conditions, and the final evidence format.

Use it for fresh-context review, regression-test-first bug fixes, parallel worktrees, CI red-to-green, release runbooks, and safe public repo launches.

Demo and repo: https://github.com/Richicinschi/awesome-agent-workflows

### Show HN draft

Show HN: Awesome Agent Workflows — practical playbooks for using coding agents safely

I’ve been collecting the workflows that make AI coding agents actually usable: how to write task briefs, split work across parallel agents, force verification before "done", run fresh-context code reviews, and launch public repos without spam.

This is intentionally tool-agnostic. It should work with Claude Code, Codex CLI, Cursor agents, Aider, OpenCode, LangGraph/CrewAI-style agents, or custom tool-using assistants.

I’d love feedback from people using agents in real repos: what workflow prevented the most damage or saved the most time?


## Example-led launch snippets

Use specific workflow examples instead of generic star requests.

### Fresh-context review snippet

AI-generated PRs can look convincing even when they skipped verification. This workflow treats the agent summary as untrusted and checks the diff, tests, and evidence from a fresh context.

### Parallel agents snippet

Running three agents at once is easy. Integrating them without branch chaos is the hard part. The parallel-agent and worktree-lane workflows show how to split scope, isolate branches, and verify integration.

### CI failure snippet

Do not rerun CI until it turns green and call that fixed. The CI red-to-green workflow forces a reproducer, explains environment deltas, and blocks weakening checks without approval.

### Public repo launch snippet

The repo-growth workflow is explicitly anti-spam: no fake stars, no paid engagement, no comment spam. It focuses on packaging, examples, contribution paths, and launch copy that asks for feedback.
