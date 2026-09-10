---
type: agent_identity_protocol
version: 1
status: active
updated: 2026-07-07
project: Agent_Handoff
---

# Agent Identity Protocol

This file defines how AI agents name themselves during parallel work.

Current work ownership lives in GitHub Issues, Pull Requests, labels, branches, and handoffs.

Each agent run should use:

- `agent_name` — human-readable name.
- `agent_id` — short slug for this repository.
- `run_id` — unique id for the current session.

Example:

```text
Agent: North Fox
Agent ID: north-fox-7c2a
Run ID: 20260702-issue-14-a91f
```

Recommended agent id format:

```text
<two-words-slug>-<4-hex>
```

Recommended run id format:

```text
YYYYMMDD-issue-<number>-<4-hex>
```

Repeat `agent_name`, `agent_id`, and `run_id` in work claim, Draft PR, handoff metadata, and handoff index when relevant.

Do not keep an active agent registry in `ai/`.
