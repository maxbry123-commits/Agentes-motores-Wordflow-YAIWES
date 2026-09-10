# Agent Tool Comparison Matrix

This is a workflow-fit matrix, not a vendor ranking.

| Tool style | Best fit | Watch out for | Start with |
| --- | --- | --- | --- |
| Claude Code | multi-step repo work, planning, review, refactors | confident summaries without fresh verification | [`01`](../../workflows/01-spec-to-plan.md), [`04`](../../workflows/04-fresh-context-code-review.md), [`15`](../../workflows/15-golden-master-refactor.md) |
| Codex CLI | terminal-native implementation and debugging | scope drift after broad repo inspection | [`12`](../../workflows/12-agent-task-contract.md), [`13`](../../workflows/13-regression-test-first-bugfix.md), [`19`](../../workflows/19-ci-red-to-green.md) |
| Cursor agents | IDE-aware edits and fast review loops | unsaved buffers and broad file edits | [`11`](../../workflows/11-change-impact-map.md), [`16`](../../workflows/16-patch-intake-triage.md), [`39`](../../workflows/39-agent-written-docs-review.md) |
| Aider | focused patching with selected files | too many files weaken boundaries | [`12`](../../workflows/12-agent-task-contract.md), [`13`](../../workflows/13-regression-test-first-bugfix.md), [`21`](../../workflows/21-dependency-upgrade-shepherd.md) |
| OpenCode | terminal workflows and agentic coding loops | tool permissions and destructive commands | [`35`](../../workflows/35-git-worktree-agent-lanes.md), [`36`](../../workflows/36-context-compaction-handoff.md), [`40`](../../workflows/40-long-running-task-checkpoint.md) |
| Local/self-hosted agents | privacy-sensitive tasks and offline stacks | weaker reasoning on high-risk review | [`09`](../../workflows/09-local-ai-stack.md), [`32`](../../workflows/32-agent-memory-hygiene-review.md), [`37`](../../workflows/37-mcp-tool-integration-review.md) |
| Framework agents | repeatable workflows and automation | hidden state, retries, and side effects | [`30`](../../workflows/30-workflow-evaluation-harness.md), [`31`](../../workflows/31-prompt-policy-change-control.md), [`37`](../../workflows/37-mcp-tool-integration-review.md) |

## Official docs and high-quality references

- [Anthropic Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [OpenAI Codex repository](https://github.com/openai/codex)
- [Cursor docs](https://docs.cursor.com/)
- [Aider docs](https://aider.chat/docs/)
- [OpenCode repository](https://github.com/sst/opencode)
- [LangGraph repository](https://github.com/langchain-ai/langgraph)
- [CrewAI repository](https://github.com/crewAIInc/crewAI)

## Selection rule

Pick the workflow based on risk first, then tool fit. A high-risk task should use the security, release, migration, memory, or tool-integration workflow even if the agent tool has a convenient shortcut.
