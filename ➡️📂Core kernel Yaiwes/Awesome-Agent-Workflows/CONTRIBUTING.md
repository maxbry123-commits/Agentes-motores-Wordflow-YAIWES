# Contributing

Thanks for improving Awesome Agent Workflows.

## What to add

Good PRs usually add one of these:

- a workflow card in `workflows/`;
- a reusable agent brief in `templates/`;
- a high-quality resource link with an explanation;
- a failure mode and guardrail from real agent work;
- a correction to unclear wording or broken links.

## Workflow contribution checklist

- [ ] The workflow has a clear trigger.
- [ ] The agent brief is copy-pasteable.
- [ ] The steps are ordered and bounded.
- [ ] Verification evidence is explicit.
- [ ] Human approval gates are stated.
- [ ] The workflow avoids vendor lock-in unless vendor-specific behavior is essential.

## Local checks

Run:

```bash
python3 scripts/lint_repo.py
```

## Style

- Be concrete.
- Prefer commands, checklists, and examples over theory.
- Do not include secrets, private customer data, or proprietary prompts.
- Avoid hype. Explain the operational value.

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the next high-value contribution clusters.
