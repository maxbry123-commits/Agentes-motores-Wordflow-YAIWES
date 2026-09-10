# Workflows

Scenario playbooks **for the agent**. These are not slash-commands for the researcher — the researcher simply says "let's get started" / "let's do the report," and the agent picks the right workflow from context.

Each workflow describes:
- **Trigger**: when the agent decides on its own to apply this scenario.
- **Preconditions**: what must already be in the project.
- **Sequence**: which skills to invoke, in what order.
- **Expected artifacts**: what should exist after the pass.
- **Failure modes**: what can go wrong and how to react.

## List of workflows

| File | When |
|---|---|
| `full-assistive.md` | New project, researcher filled out `project-config.yaml` with `mode: assistive`. Full cycle with human pauses. |
| `full-autonomous.md` | The same full cycle, but `mode: autonomous`. No pauses, with a final human gate. |
| `audit-external.md` | An external agency sent over interviews and a report. Re-check their work. |
| `desk-only.md` | The researcher wants "what do we know about topic X." No interviews. |
| `analyze-only.md` | Transcripts already exist, only stages 7–9 are needed. |

If a situation fits none of these — combine parts or write your own ad-hoc flow.
