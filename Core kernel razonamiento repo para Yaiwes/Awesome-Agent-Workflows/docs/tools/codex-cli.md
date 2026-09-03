# Codex CLI

Use workflow cards as the task instruction for a bounded Codex run. Include branch, allowed files, and exact verification commands.

## Best starting workflows

- Great fit for implementation, debugging, and test-driven loops.
- Prefer smaller tasks and explicit stop conditions.
- Use `agent-workflows.json` to select cards programmatically.

## Gotchas

- Do not let the agent broaden scope after inspecting the repo.
- Verify diffs and commands yourself before merging.

## Recommended starter brief

```text
Use the selected workflow exactly. Stay within the allowed files. Record evidence from commands or files. Stop if the task needs secrets, production access, destructive commands, or a wider scope.
```

## Official reference

- [OpenAI Codex repository](https://github.com/openai/codex)
