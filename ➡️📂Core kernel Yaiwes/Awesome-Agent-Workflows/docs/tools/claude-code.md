# Claude Code

Paste the workflow into the Claude Code session before asking for implementation. Keep repository paths and verification commands explicit.

## Best starting workflows

- Use workflow cards as task briefs.
- Ask for a plan before code on ambiguous changes.
- Run fresh-context review before merge.

## Gotchas

- Claude may be confident before evidence exists.
- Long sessions need handoffs and checkpoints.

## Recommended starter brief

```text
Use the selected workflow exactly. Stay within the allowed files. Record evidence from commands or files. Stop if the task needs secrets, production access, destructive commands, or a wider scope.
```

## Official reference

- [Claude Code official docs](https://docs.anthropic.com/en/docs/claude-code)
