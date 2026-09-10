# Provenance and attribution

## Five distinct provenance layers

| Layer | Examples | Public rule |
|---|---|---|
| Personal public work | source, tests, synthetic examples, architecture, and documentation in this repository | directed, reviewed, and maintained by Wanrun Cong under Apache-2.0; programming-agent assistance is disclosed |
| Historical competition context | project-level cases, scores, rulings, and lessons from the author's participation | reported as bounded context; original submissions are not included or claimed as sole-authored work |
| Development-time programming agents | implementation, debugging, review, and documentation assistance | disclosed as assistance; Wanrun Cong retains responsibility |
| Runtime LLM/planner | bounded proposals or control in particular versions | recorded only when task/version evidence supports it; no unsupported score attribution |
| Scientific backends | docking, retrosynthesis, folding, sampling, training | named with upstream provenance and separate code/weight/data terms |

## Why model names are not score explanations

A score attribution requires, at minimum:

```text
task + immutable image/version + runtime model configuration +
successful call log + output identity + platform score
```

The available historical evidence does not close this chain for every highest-scoring version. Runtime model settings also changed across development. The public narrative therefore says “replaceable LLM/planner” unless stronger version-specific evidence is available.

## Personal project provenance

Wanrun Cong created the code, tests, synthetic examples, evidence model, and technical documentation for this personal research project, with the development-time programming-agent assistance disclosed above. The case studies were independently written from factual summaries and evidence audits rather than copied from task-specific or provenance-uncertain competition source.

The publication boundary means personal implementation, explicit provenance review, and no transfer of restricted artifacts. It is not a claim of ownership over original competition submissions or third-party scientific systems.

Excluded by design:

- Git history and large-file objects from historical competition work;
- original task prompts, raw logs, outputs, checkpoints, and submission packages;
- internal endpoints, credentials, infrastructure details, and image identities;
- official data and authenticated attachments;
- third-party source and weights without closed provenance and redistribution rights;
- the two task4 training tools ruled out of bounds.

## Citation

Use [CITATION.cff](../CITATION.cff) for this personal public repository. Cite upstream scientific systems separately according to their own requested citations and the exact versions you use.
