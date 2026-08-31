# agent-resume

[![PyPI](https://img.shields.io/badge/pypi-agent--resume-blue)](https://pypi.org/project/agent-resume/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)

Checkpoint and resume long-running AI agent jobs. Your agent is processing 100 GitHub issues, crashes on issue 47, and the next run picks up at issue 48 instead of starting over. Zero runtime dependencies.

Built for the obvious failure mode: an agent that has to do a lot of small things in a row, and you do not want a single timeout, OOM, dropped connection, or deploy to throw away an hour of work.

## Install

```bash
pip install agent-resume
```

Zero runtime dependencies. Python 3.10+.

## 60-second quickstart

```python
from agent_resume import JsonlStore, resume_or_start

store = JsonlStore("agent.ckpt")

def process_issue(issue_id, state):
    # do the actual work: call an LLM, post a comment, update Notion
    results = dict(state.get("results") or {})
    results[str(issue_id)] = f"summary for #{issue_id}"
    return {**state, "results": results}

run = resume_or_start(
    store=store,
    initial_state={"results": {}},
    work_items=list(range(1, 101)),
)

for issue_id in run:
    new_state = process_issue(issue_id, run.state)
    run.checkpoint(new_state)   # appended to the JSONL store, fsync'd
```

If the process dies at issue 47, just run the same script again. `resume_or_start()` finds the existing checkpoint, restores `run.state`, and the loop yields items 48..100. The first 47 are skipped.

## What it does

- **One checkpoint per turn.** After each work item, you call `run.checkpoint(new_state)`. The store appends a row and fsyncs.
- **Skip-on-resume.** Items already in `completed_items` are not re-yielded. You decide the item identity via `item_key`.
- **At-least-once, not exactly-once.** If you crash mid-item, that item replays on the next run. Build idempotent workers.
- **JSONL store by default.** Append-only, one Checkpoint per line, durable, greppable. Swap in your own `Sink` for Redis or SQLite if you need it.
- **Zero deps.** Standard library only. No DB driver, no cloud SDK, nothing.

## When this is not what you want

`agent-resume` is for one-shot agent jobs that process a known list of items. If you need something different, reach for a sibling library:

| Library | Use it when |
|---|---|
| **`agent-resume`** (this one) | A run has a known list of work items and you want to resume after a crash. |
| [`agentmemory`](https://github.com/MukundaKatta/agentmemory) | The agent needs to pull historical facts on demand across many runs (long-lived memory store). |
| [`agentsnap`](https://github.com/MukundaKatta/agentsnap) | You want snapshot-style tests that assert "this run produced this tool-call trace". |
| [`agent-decision-log`](https://github.com/MukundaKatta/agent-decision-log) | You want a "why" audit layer over each LLM call (decisions, not state). |

`agent-resume` writes one row per turn and replays from the last one. It is not a database, not a memory layer, not a tracing tool. If you want any of those, the right pick is above.

## API reference

### `resume_or_start(*, store, initial_state=None, work_items=(), item_key=None) -> Resumable`

The main entry point. Opens or resumes a checkpointed run.

- `store`: any object implementing the `Sink` protocol. The library ships `JsonlStore` and `InMemoryStore`.
- `initial_state`: starting state if no checkpoint exists. Ignored when resuming; the stored state wins.
- `work_items`: ordered sequence of items to process. The `Resumable` yields each one that has not been marked complete.
- `item_key`: function to extract a comparable id from each work item. Defaults to the item itself.

Returns a `Resumable`. Check `.resumed` to know whether it picked up an existing run.

### `Resumable`

- `state` - rolling state dict.
- `turn` - count of checkpoints written so far.
- `completed_items` - list of item ids already done.
- `resumed` - True if loaded from store.
- `remaining_items()` - the items still left to process.
- `__iter__()` - yields each remaining work item.
- `checkpoint(new_state=None) -> Checkpoint` - persist a new checkpoint and advance turn.

### `JsonlStore(path, *, fsync=True)`

Append-only JSONL file backed store. One Checkpoint per line. fsync-on-write by default.

- `append(checkpoint)` - write one checkpoint.
- `iter_checkpoints()` - stream every checkpoint in order.
- `load_latest()` - return the last checkpoint, or raise `NoCheckpoint`.
- `__len__()` - count of rows.

Process-local lock only. If two processes write to the same path you need a file lock or a different store.

### `InMemoryStore`

Same surface as `JsonlStore` but non-durable. Useful for tests and demos.

### `Checkpoint`

Dataclass with `turn`, `state`, `completed_items`, `timestamp`. Provides `to_json()` and `from_json()` for the JSONL line format.

### Exceptions

- `CheckpointCorrupt(message, *, line_number=None)` - raised when a JSONL line cannot be parsed.
- `NoCheckpoint` - raised by `Store.load_latest()` when the store is empty.

## Sibling libs in the agent-stack family

This is one of a small set of zero-dep Python and Rust libs aimed at AI agent operators:

- [`agentleash`](https://github.com/MukundaKatta/agentleash) - money + egress safety harness
- [`birddog`](https://github.com/MukundaKatta/birddog) - audited Bright Data egress for scrapers
- [`tool-call-budgets`](https://github.com/MukundaKatta/tool-call-budgets) - per-tool call-count caps
- [`token-budget-py`](https://github.com/MukundaKatta/token-budget-py) - token + USD budget
- [`agentvet`](https://github.com/MukundaKatta/agentvet) - validate tool args before execution
- [`agenttrace`](https://github.com/MukundaKatta/agenttrace) - cost + latency tracking

Same shape: small, single-purpose, zero deps, BYO-LLM. Pick the ones you need.

## Examples

See `examples/`:

- `examples/process_issues_with_resume.py` - basic loop with checkpointing. Run twice to see resume.
- `examples/crash_recovery_demo.py` - simulates a crash mid-run, then resumes and finishes in a second pass. Self-contained, no external state.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Targets a 30+ test suite covering checkpoint serialization, JSONL store durability, in-memory store, corrupt-line handling, fresh start, resume, concurrent writes, and end-to-end crash recovery.

## License

MIT. See [LICENSE](LICENSE).
