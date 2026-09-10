# OpenCode

Use workflow cards as reusable task prompts for terminal-native coding work.

## Best starting workflows

- Good fit for repo operations and structured handoffs.
- Keep tool permissions and shell commands bounded.
- Use Long-Running Task Checkpoint for slow commands.

## Gotchas

- Be explicit about destructive commands and public side effects.
- Do not pass secrets through prompts.

## Recommended starter brief

```text
Use the selected workflow exactly. Stay within the allowed files. Record evidence from commands or files. Stop if the task needs secrets, production access, destructive commands, or a wider scope.
```

## Official reference

- [OpenCode repository](https://github.com/sst/opencode)
