# Cursor agents

Paste the workflow into the chat or agent instruction, then pin relevant files before execution.

## Best starting workflows

- Use for codebase-aware edits and review passes.
- Keep accepted files small and inspect generated changes.
- Pair with Fresh-Context Code Review for PRs.

## Gotchas

- IDE state can hide untracked files or unsaved buffers.
- Agent edits may be broader than the prompt suggests.

## Recommended starter brief

```text
Use the selected workflow exactly. Stay within the allowed files. Record evidence from commands or files. Stop if the task needs secrets, production access, destructive commands, or a wider scope.
```

## Official reference

- [Cursor official docs](https://docs.cursor.com/)
