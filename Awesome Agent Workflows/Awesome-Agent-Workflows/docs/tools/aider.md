# Aider

Use the workflow as the natural-language task brief and add only files the agent is allowed to edit.

## Best starting workflows

- Excellent for focused patch work.
- Use Change Impact Map before adding many files.
- Use Regression-Test-First Bug Fix for bug reports.

## Gotchas

- Adding too many files weakens scope control.
- Run the verification command outside the agent too.

## Recommended starter brief

```text
Use the selected workflow exactly. Stay within the allowed files. Record evidence from commands or files. Stop if the task needs secrets, production access, destructive commands, or a wider scope.
```

## Official reference

- [Aider official docs](https://aider.chat/docs/)
