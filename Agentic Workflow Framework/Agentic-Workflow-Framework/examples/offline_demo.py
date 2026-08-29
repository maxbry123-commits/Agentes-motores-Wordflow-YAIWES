"""Offline, deterministic demo — runs with NO API key and NO network.

This script exercises the *entire* framework against the
:class:`MockLLMBackend`, so you can see the Manager/Worker model, checkpointing,
clean stop/resume, and the self-improvement loop in action without spending a
token. Every "model" response below is a fixed canned reply; the orchestration
around it is the real framework code.

Run it with::

    python -m examples.offline_demo

For the same workflow against the real Claude API, see
``examples/support_triage_workflow.py``.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

from agentic_workflow import CheckpointStore, Manager, MockLLMBackend, SharedState

from .workers import SAMPLE_TICKET, build_pipeline

# A short first draft (fails the evaluator) and a strong second draft (passes).
WEAK_REPLY = "We'll look into the duplicate charge soon."
STRONG_REPLY = (
    "Hi there, thank you for flagging this and I'm sorry for the repeated "
    "frustration. I can confirm this is a billing issue: you were charged twice "
    "for your Acme Analytics Pro plan (version 3.2) this cycle. I've submitted a "
    "refund for the duplicate $49 charge, which should land within 5-7 business "
    "days, and I've added a safeguard so the double charge won't recur next "
    "month. Please let me know if there's anything else I can do."
)


def build_mock_backend() -> MockLLMBackend:
    """Register one deterministic handler per worker (and the improver)."""
    backend = MockLLMBackend()

    backend.register(
        "classifier",
        lambda idx, ctx, prompt: {
            "category": "billing",
            "urgency": "high",
            "sentiment": "negative",
        },
    )
    backend.register(
        "extractor",
        lambda idx, ctx, prompt: {
            "product": "Acme Analytics Pro",
            "affected_version": "3.2",
            "requested_action": "refund the duplicate $49 charge",
        },
    )
    # The responder returns a weak reply first, then a strong one on the re-run
    # triggered by self-improvement. ``idx`` is the zero-based call count.
    backend.register(
        "responder",
        lambda idx, ctx, prompt: {
            "reply": WEAK_REPLY if idx == 0 else STRONG_REPLY,
            "internal_note": "Duplicate billing charge; refund issued.",
        },
    )
    # The improvement meta-call (purpose="improvement") returns a better
    # instruction. The Manager validates and applies it before the re-run.
    backend.register(
        "responder",
        lambda idx, ctx, prompt: {
            "improved_instruction": (
                "Write a warm, specific reply to the customer. Open with a "
                "greeting, acknowledge the problem, name the issue type and the "
                "product/version, state the concrete action you have taken, and "
                "set a clear expectation for resolution."
            )
        },
        purpose="improvement",
    )
    return backend


def _print_header(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


def main() -> None:
    pipeline = build_pipeline()
    backend = build_mock_backend()

    with tempfile.TemporaryDirectory(prefix="awf-demo-") as tmp:
        store = CheckpointStore(Path(tmp) / "checkpoints")
        state = SharedState({"ticket": SAMPLE_TICKET})

        manager = Manager(
            pipeline,
            backend,
            state=state,
            checkpoint_store=store,
            run_id="ticket-demo",
            max_improvement_rounds=2,
        )

        _print_header("PHASE 1 — run only the first step, then STOP")
        manager.run(max_steps=1)
        print(f"cursor after stop: {manager.cursor}/{len(pipeline)} "
              f"(next step: {manager.next_step_name})")
        print("classification in shared state:")
        print(json.dumps(state.get("classification"), indent=2))
        print(f"checkpoint written to: {store._path('ticket-demo')}")

        _print_header("PHASE 2 — RESUME in a fresh Manager/pipeline/backend")
        # Simulate a brand-new process: rebuild everything from scratch and
        # restore from the checkpoint on disk.
        fresh_pipeline = build_pipeline()
        fresh_backend = build_mock_backend()
        resumed = Manager.resume(fresh_pipeline, fresh_backend, store, "ticket-demo")
        print(f"resumed at cursor {resumed.cursor}/{len(fresh_pipeline)} "
              f"(next step: {resumed.next_step_name})")

        resumed.run()  # finish extractor + responder (with self-improvement)

        _print_header("RESULT")
        final_state = resumed.state
        print("extraction:")
        print(json.dumps(final_state.get("extraction"), indent=2))
        print("\nfinal reply:")
        print(json.dumps(final_state.get("reply"), indent=2))

        responder = fresh_pipeline.worker_by_name("responder")
        print(f"\nresponder instruction version: {responder.instruction_version} "
              f"(0 = never improved)")

        _print_header("SELF-IMPROVEMENT LOG")
        if resumed.log:
            for entry in resumed.log:
                print(json.dumps(entry))
        else:
            print("(no improvement was needed)")

        _print_header("EXECUTION HISTORY (audit trail)")
        for event in final_state.history:
            print(json.dumps(event.to_dict()))


if __name__ == "__main__":
    main()
