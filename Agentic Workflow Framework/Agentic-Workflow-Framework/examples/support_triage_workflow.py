"""Live end-to-end demo against the real Claude API.

This runs the same three-stage triage pipeline as ``offline_demo.py``, but with
:class:`AnthropicBackend` instead of the mock. Each worker is answered by Claude
using structured outputs, and the responder step's self-improvement loop will
ask Claude to refine its own instruction if the first draft scores below the
threshold.

Requirements:

* ``pip install anthropic``
* ``export ANTHROPIC_API_KEY=...``  (the key is read from the environment by the
  SDK — it is never hardcoded here)

Usage::

    python -m examples.support_triage_workflow
    python -m examples.support_triage_workflow "Subject: ...your own ticket..."

If ``ANTHROPIC_API_KEY`` is not set, the script prints instructions and exits
without making any network call — run ``examples/offline_demo.py`` to see the
full machinery without a key.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from agentic_workflow import (
    AnthropicBackend,
    CheckpointStore,
    Manager,
    SharedState,
)

from .workers import SAMPLE_TICKET, build_pipeline


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set.\n"
            "  - Set it:    export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  - Or run the offline demo (no key needed):\n"
            "        python -m examples.offline_demo",
            file=sys.stderr,
        )
        return 1

    ticket = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_TICKET

    pipeline = build_pipeline()
    backend = AnthropicBackend(model="claude-opus-4-8", effort="high")
    state = SharedState({"ticket": ticket})

    with tempfile.TemporaryDirectory(prefix="awf-live-") as tmp:
        store = CheckpointStore(Path(tmp) / "checkpoints")
        manager = Manager(
            pipeline,
            backend,
            state=state,
            checkpoint_store=store,
            run_id="ticket-live",
            max_improvement_rounds=2,
        )

        print("Running triage pipeline against Claude ...\n")
        manager.run()

        print("classification:")
        print(json.dumps(state.get("classification"), indent=2))
        print("\nextraction:")
        print(json.dumps(state.get("extraction"), indent=2))
        print("\nreply:")
        print(json.dumps(state.get("reply"), indent=2))

        responder = pipeline.worker_by_name("responder")
        print(
            f"\nresponder instruction version: {responder.instruction_version} "
            f"(>0 means the self-improvement loop refined it)"
        )
        if manager.log:
            print("\nself-improvement log:")
            for entry in manager.log:
                print(json.dumps(entry))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
