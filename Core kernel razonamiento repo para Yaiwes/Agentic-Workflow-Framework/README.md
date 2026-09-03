# agentic-workflow-framework

A lightweight, dependency-light **multi-agent workflow framework** in Python. A
stateful **Manager** orchestrates specialized, single-responsibility **Worker**
agents through a defined **Pipeline**, communicating through a shared state
store, with **clean stop/resume via checkpointing** and an optional
**self-improvement loop** in which the Manager refines a Worker's prompt based on
measured results — *without ever touching the Worker's protected core*.

LLM calls go through the official [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
(Claude). The API key is read from the `ANTHROPIC_API_KEY` environment variable;
no key or secret is ever hardcoded.

> **Try it in 5 seconds, no API key:** `python -m examples.offline_demo`

---

## What AI-engineering skill does this demonstrate?

This project is a compact but complete example of **agentic system design** — the
discipline of composing LLM calls into a reliable, inspectable, recoverable
system rather than a single prompt. Concretely:

- **Multi-agent decomposition.** One hard task is split into small, single-
  responsibility workers that each do exactly one thing and validate their own
  inputs and outputs.
- **A safety boundary between "what's fixed" and "what's tunable"** — the
  protected-core-vs-mutable-method idea (below). This is the part most ad-hoc
  agent code gets wrong: it lets a prompt tweak silently break the data contract.
- **Closed-loop self-improvement.** The system measures its own output and asks
  the model to improve the *instruction* of an under-performing worker, bounded
  and reconciled so a regression can never leak downstream.
- **Operational robustness.** Shared state, an audit trail, atomic checkpoints,
  and clean stop/resume — the things that separate a demo from something you can
  actually run.
- **Provider-correct, structured LLM usage.** Structured outputs to guarantee
  each worker's JSON contract, adaptive thinking, and a clean backend seam that
  makes the whole thing runnable offline for tests and demos.

---

## The Manager / Worker model

```
Manager  ──drives──▶  Pipeline = [ Step(classifier), Step(extractor), Step(responder, eval) ]
   │                                   │            │             │
   │ owns: cursor, log, checkpoints    ▼            ▼             ▼
   │                                Worker       Worker        Worker
   │                                   │  read/write only via   │
   └──────────────────────────────▶  SharedState  ◀────────────┘
```

- **Worker** — a single-responsibility agent. It declares the state keys it
  reads (`input_keys`), where it writes (`output_key`), the JSON shape it must
  produce (`output_schema`), and a free-text `default_instruction`. It does one
  job and never talks to other workers directly.
- **SharedState** — a JSON-serializable key/value store with an append-only event
  log. It is the *only* channel between workers, which keeps the data-flow
  explicit and auditable.
- **Pipeline / Step** — the static, ordered list of workers. Each step can carry
  an evaluator and a quality threshold.
- **Manager** — the stateful orchestrator. It walks the pipeline, records an
  audit event per step, checkpoints after each, runs the self-improvement loop
  when a step underperforms, and supports stop/resume.

## The protected core vs. the mutable method

This is the core architectural idea and the framework's main safety property.

Every `Worker` is split in two:

| | Protected core | Mutable method |
|---|---|---|
| **What** | `run`, `render_prompt`, `build_system`, output validation, state writes | the free-text `instruction` |
| **Does** | validate inputs → build prompt → call backend → validate output vs. schema → write state | guides *how* the worker does the job well |
| **Who can change it** | nobody — `@final` **and** a runtime guard reject any subclass that overrides it | only `propose_instruction()`, which validates and versions the change |

The framework — not the instruction — always owns the `[INPUTS]` rendering and
the `[OUTPUT CONTRACT]` schema inside each prompt. So when the self-improvement
loop rewrites a worker's instruction, it can change the worker's *quality* but it
**structurally cannot** change which inputs it reads, where it writes, or the
shape of its output. Tuning can make a worker better; it can never make it break
the pipeline.

Trying to override the core fails loudly, at class-definition time:

```python
class Bad(Worker):
    name = "bad"; output_key = "x"; default_instruction = "do"
    def run(self, *a, **k): ...      # raises ProtectedCoreError
```

## Stop / resume via checkpointing

The Manager serializes everything dynamic — shared state, the cursor, each
worker's mutable instruction, and the log — to an atomic JSON checkpoint after
every step. A run can be stopped (`max_steps=`, `stop_before=`) and rebuilt in a
fresh process:

```python
manager.run(max_steps=1)                                 # stop after step 1
# ... later, anywhere ...
resumed = Manager.resume(pipeline, backend, store, run_id)
resumed.run()                                            # finish the rest
```

Because the protected core lives only in code (never in the checkpoint), a
resumed run is guaranteed to honor the same contracts as the original. Any
self-improvement that happened before the stop is restored and carried forward.
See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the checkpoint format.

---

## Install

```bash
git clone <this-repo>
cd agentic-workflow-framework

# Core framework + offline demo + tests need no third-party packages.
# For the live Claude backend:
pip install -r requirements.txt        # installs `anthropic`
export ANTHROPIC_API_KEY=sk-ant-...     # read from the env, never hardcoded
```

Python 3.9+.

---

## Usage

### Run the offline demo (no API key)

```bash
python -m examples.offline_demo
```

It runs the full three-stage support-triage pipeline against a deterministic mock
backend, **stops after the first step**, **resumes from disk in a fresh
Manager/pipeline/backend**, and shows the **self-improvement loop** lift the
responder's score from `0.0` to `1.0` by refining only its mutable instruction
(version `0 → 1`). Abridged output:

```
PHASE 1 — run only the first step, then STOP
cursor after stop: 1/3 (next step: extractor)

PHASE 2 — RESUME in a fresh Manager/pipeline/backend
resumed at cursor 1/3 (next step: extractor)

SELF-IMPROVEMENT LOG
{"event": "improvement_round", "worker": "responder", "round": 1,
 "score_before": 0.0, "score_after": 1.0, "instruction_version": 1}
```

### Run the live workflow (real Claude)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python -m examples.support_triage_workflow
# or pass your own ticket:
python -m examples.support_triage_workflow "Subject: I can't log in ..."
```

### A concrete, complete example

A three-worker pipeline that triages a customer-support ticket — classify →
extract → draft a reply, with a quality gate that triggers self-improvement on
the reply. (Full version in [`examples/workers.py`](examples/workers.py).)

```python
from agentic_workflow import (
    AnthropicBackend, CheckpointStore, EvalResult, Manager,
    Pipeline, SharedState, Step, Worker, WorkerResult,
)

class ClassifierWorker(Worker):
    name = "classifier"
    input_keys = ("ticket",)
    output_key = "classification"
    output_schema = {
        "type": "object",
        "properties": {
            "category": {"type": "string",
                         "enum": ["billing", "technical", "account", "other"]},
            "urgency":  {"type": "string",
                         "enum": ["low", "medium", "high", "critical"]},
        },
        "required": ["category", "urgency"],
        "additionalProperties": False,
    }
    default_instruction = "Classify the ticket's category and urgency."

class ResponderWorker(Worker):
    name = "responder"
    input_keys = ("ticket", "classification")
    output_key = "reply"
    output_schema = {
        "type": "object",
        "properties": {"reply": {"type": "string"}},
        "required": ["reply"],
        "additionalProperties": False,
    }
    default_instruction = "Write a reply to the customer."

def responder_eval(result: WorkerResult, state: SharedState) -> EvalResult:
    reply = result.output.get("reply", "")
    return EvalResult(
        score=1.0 if len(reply) >= 220 else 0.0,
        feedback="Acknowledge the issue and set a clear expectation.",
    )

pipeline = Pipeline([
    Step(ClassifierWorker()),
    Step(ResponderWorker(), evaluator=responder_eval, improve_threshold=0.9),
])

backend = AnthropicBackend(model="claude-opus-4-8")          # reads ANTHROPIC_API_KEY
store   = CheckpointStore("./checkpoints")
state   = SharedState({"ticket": "I was charged twice this month, please refund."})

manager = Manager(pipeline, backend, state=state,
                  checkpoint_store=store, run_id="ticket-1")
manager.run()                                                # stop/resume-able

print(state.get("classification"))
print(state.get("reply"))
```

Swap `AnthropicBackend` for `MockLLMBackend` (with registered handlers) to run
the identical pipeline offline — that one-line change is all the test suite and
the offline demo do.

---

## Project layout

```
agentic_workflow/
  __init__.py        public API
  state.py           SharedState + audit event log
  worker.py          Worker base: protected core + mutable instruction
  pipeline.py        Pipeline, Step, EvalResult
  manager.py         Manager: orchestration, self-improvement, stop/resume
  improvement.py     the instruction-refinement meta-call
  checkpoint.py      atomic JSON checkpoint store
  llm.py             LLMBackend protocol; AnthropicBackend + MockLLMBackend
  errors.py          typed exception hierarchy
examples/
  workers.py                    the three triage workers + evaluator + pipeline
  offline_demo.py               full run with the mock backend (no key)
  support_triage_workflow.py    full run with real Claude
tests/
  test_framework.py             13 offline tests (pytest)
docs/
  ARCHITECTURE.md
```

## Testing

```bash
pip install pytest
pytest -q          # 13 passed — runs fully offline, no API key, no network
```

---

## Design notes & honesty

- **Claude API usage.** Workers request [structured outputs](https://docs.claude.com)
  (`output_config.format`) so each response is guaranteed to match the worker's
  JSON schema; the backend also enables adaptive thinking and an `effort` setting.
  Model defaults to `claude-opus-4-8`.
- **The evaluator in the examples is deliberately simple** (length + keyword +
  greeting heuristics) so the self-improvement loop is fully deterministic and
  easy to watch. In a real system you would plug in an LLM-as-judge or human
  feedback — the `Evaluator` seam is the same.
- **The mock backend's replies are canned**, by design: it exists to exercise the
  *orchestration* (state, contracts, checkpoints, the improvement loop) without a
  network. The orchestration code it drives is the real framework.
- **No secrets in code.** Keys come from `ANTHROPIC_API_KEY` via the SDK. `.env`
  and checkpoint outputs are git-ignored.

## Credits

- Built on the official **[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)** (`anthropic`) for all Claude calls.
- Standard library only otherwise (`dataclasses`, `json`, `pathlib`, `typing`).

## License

MIT — see [`LICENSE`](LICENSE).
