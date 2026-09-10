"""Self-contained crash-recovery demo.

Runs two passes against a single checkpoint file:

1. First pass processes 5 of 10 items, then deliberately raises to
   simulate a crash. The five completed items are durably in the JSONL
   store.

2. Second pass calls `resume_or_start()` on the same file, sees the
   existing checkpoints, and yields only items 6..10.

The expected output prints a clear "before crash / after crash" boundary
so it is obvious what is going on.
"""

import tempfile
from pathlib import Path

from agent_resume import JsonlStore, resume_or_start


class SimulatedCrash(Exception):
    pass


def process_item(item_id: int, state: dict) -> dict:
    results = dict(state.get("results") or {})
    # JSON dict keys are strings, so stringify the id before stashing it.
    results[str(item_id)] = item_id * 10
    return {**state, "results": results}


def first_run(path: Path, items: list[int]) -> None:
    print("=" * 60)
    print("Pass 1: process 5 items, then simulate a crash on item 6.")
    print("=" * 60)

    store = JsonlStore(path)
    run = resume_or_start(
        store=store,
        initial_state={"results": {}},
        work_items=items,
    )
    assert not run.resumed, "expected a fresh start"

    processed_this_run = 0
    try:
        for item in run:
            print(f"  processing item {item}")
            new_state = process_item(item, run.state)
            run.checkpoint(new_state)
            processed_this_run += 1
            if processed_this_run >= 5:
                raise SimulatedCrash("process died")
    except SimulatedCrash as exc:
        print(f"\n  crash: {exc}")
        print(f"  checkpoints durably written: {len(store)}")
        print(f"  last persisted state: {store.load_latest().state}")


def second_run(path: Path, items: list[int]) -> None:
    print()
    print("=" * 60)
    print("Pass 2: re-run the same code. resume_or_start() picks up at 6.")
    print("=" * 60)

    store = JsonlStore(path)
    run = resume_or_start(
        store=store,
        initial_state={"results": {}},
        work_items=items,
    )
    assert run.resumed, "expected to resume from checkpoint"
    print(f"  resumed at turn {run.turn}, completed_items={run.completed_items}")
    print(f"  remaining: {run.remaining_items()}")

    for item in run:
        print(f"  processing item {item}")
        new_state = process_item(item, run.state)
        run.checkpoint(new_state)

    print()
    print("=" * 60)
    print(f"Final state after recovery:")
    print(f"  total turns: {run.turn}")
    print(f"  completed_items: {run.completed_items}")
    print(f"  results: {run.state['results']}")
    print("=" * 60)


def main() -> None:
    items = list(range(1, 11))  # 10 items
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "crash_demo.ckpt"
        first_run(path, items)
        second_run(path, items)


if __name__ == "__main__":
    main()
