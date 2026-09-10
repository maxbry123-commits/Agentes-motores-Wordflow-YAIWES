# Architecture

This document explains how the pieces fit together. For installation and usage,
see the top-level `README.md`.

## The data-flow picture

```
                 +-------------------------------------------------+
                 |                    Manager                       |
                 |  (stateful: cursor, log, checkpoints, run_id)    |
                 +-------------------------------------------------+
                        |            |                 |
              drives    |            | self-improve    | persist
              step N    v            v                 v
                 +-----------+   +-----------+   +-----------------+
                 |  Step     |   | improve_  |   | CheckpointStore |
                 |  (worker  |   | instruction|  | (atomic JSON)   |
                 |  + eval)  |   +-----------+   +-----------------+
                 +-----------+
                        |
                run()   v
                 +-------------------+        reads/writes
                 |     Worker        | <---------------------+
                 | protected core +  |                       |
                 | mutable method    |                       v
                 +-------------------+              +-------------------+
                        |  generate()              |   SharedState     |
                        v                          | (key/value + log) |
                 +-------------------+              +-------------------+
                 |   LLMBackend      |
                 | Anthropic / Mock  |
                 +-------------------+
```

## Components

### `SharedState` (`state.py`)
A JSON-serializable key/value store plus an append-only event log and a revision
counter. Workers communicate **only** through it — never directly with each
other. `require(key)` is the input-contract primitive: it raises a precise
`ContractViolation` when an upstream step failed to produce a needed key.

### `Worker` (`worker.py`)
The heart of the design. A worker is split into:

- **Protected core** — `run`, `render_prompt`, `build_system`, `_validate_output`,
  and the (de)serialization of its mutable state. These are marked `@final` and a
  runtime guard in `__init_subclass__` raises `ProtectedCoreError` if a subclass
  tries to redefine any of them. The core enforces: validate inputs -> assemble
  prompt -> call backend -> validate output against the JSON schema -> write to
  shared state.
- **Mutable method** — the free-text `instruction`, changed only through
  `propose_instruction`, which validates the candidate and bumps a version. This
  is the *only* part of a worker that can change at runtime.

The framework (not the instruction) owns the `[INPUTS]` rendering and the
`[OUTPUT CONTRACT]` schema in every prompt. That is the structural reason a bad
or auto-generated instruction can change *quality* but never *protocol*.

### `Pipeline` / `Step` (`pipeline.py`)
A static, name-unique, ordered list of steps. Each `Step` pairs a worker with an
optional `evaluator` and an `improve_threshold`. The cursor that walks the
pipeline lives on the Manager, not here, which keeps pipelines reusable.

### `Manager` (`manager.py`)
The stateful orchestrator. It runs steps one at a time, records an audit event
per step, and checkpoints after each. For an evaluated step it runs the
self-improvement loop (below). It can stop early (`max_steps`, `stop_before`) and
be reconstructed from a checkpoint with `Manager.resume(...)`.

### `improve_instruction` (`improvement.py`)
The self-improvement step. When a score is below threshold, it sends the backend
a meta-prompt that includes the fixed protocol and schema and asks **only** for a
rewritten instruction (returned via structured output). The Manager then offers
that candidate to `propose_instruction`, which has final say. The kept result is
always the best-scoring one, and shared state is reconciled to it, so a
regression never leaks downstream.

### `LLMBackend` (`llm.py`)
A one-method protocol. `AnthropicBackend` calls Claude through the official SDK
with structured outputs and adaptive thinking; `MockLLMBackend` returns
registered, deterministic replies so the whole framework runs offline.

## Stop / resume in detail

A checkpoint payload contains everything needed to continue:

```json
{
  "run_id": "...",
  "cursor": 1,
  "pipeline": ["classifier", "extractor", "responder"],
  "state": { "data": { ... }, "history": [ ... ], "revision": 7 },
  "workers": { "responder": { "instruction": "...", "version": 1, "history": [...] } },
  "log": [ ... ]
}
```

`Manager.resume(pipeline, backend, store, name)`:

1. Loads the payload and verifies the provided pipeline structurally matches the
   saved one (same worker names, same order) — else `CheckpointError`.
2. Rebuilds `SharedState` from `state`.
3. Restores each worker's **mutable instruction** from `workers`, so any
   self-improvement that happened before the stop is carried forward.
4. Restores the cursor and log.

Because the protected core lives entirely in code (never in the checkpoint), a
resumed run is guaranteed to honor the same I/O contracts as the original.
