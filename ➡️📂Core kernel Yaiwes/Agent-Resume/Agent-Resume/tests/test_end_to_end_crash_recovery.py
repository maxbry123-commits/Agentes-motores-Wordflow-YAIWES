"""End-to-end crash recovery test.

Simulates a long-running agent job that crashes partway, then re-runs from
the same checkpoint file and finishes without redoing completed work.
"""

import pytest

from agent_resume import JsonlStore, resume_or_start


class SimulatedCrash(Exception):
    """Raised by the worker to simulate a process death."""


def _process_item(item_id: int, state: dict) -> dict:
    """A toy worker. Squares the input and stashes it in state.

    Note: keys are stringified because the state will round-trip through
    JSON on restore. JSON dict keys are strings; that is JSON's rule, not
    ours. Workers that need int keys should stringify on write and parse
    on read.
    """
    results = dict(state.get("results") or {})
    results[str(item_id)] = item_id * item_id
    return {**state, "results": results, "last": item_id}


def _run_until(path, items, crash_after: int | None) -> list[int]:
    """Execute the run, optionally raising SimulatedCrash after N items."""
    store = JsonlStore(path)
    run = resume_or_start(
        store=store,
        initial_state={"results": {}},
        work_items=items,
    )
    processed_this_run: list[int] = []
    for item in run:
        new_state = _process_item(item, run.state)
        run.checkpoint(new_state)
        processed_this_run.append(item)
        if crash_after is not None and len(processed_this_run) >= crash_after:
            raise SimulatedCrash(f"died after {crash_after}")
    return processed_this_run


def test_end_to_end_crash_recovery(tmp_path):
    path = tmp_path / "issues.ckpt"
    items = list(range(1, 11))  # 10 items

    # First attempt: process 5 then "crash".
    with pytest.raises(SimulatedCrash):
        _run_until(path, items, crash_after=5)

    # Verify five checkpoints were durably written.
    store = JsonlStore(path)
    assert len(store) == 5
    assert store.load_latest().completed_items == [1, 2, 3, 4, 5]

    # Second attempt: same code, should pick up at item 6.
    processed = _run_until(path, items, crash_after=None)
    assert processed == [6, 7, 8, 9, 10]

    # Final state has all 10 squared results.
    final = JsonlStore(path).load_latest()
    assert final.state["results"] == {str(i): i * i for i in range(1, 11)}
    assert final.completed_items == list(range(1, 11))


def test_resume_after_three_separate_crashes(tmp_path):
    path = tmp_path / "issues.ckpt"
    items = list(range(1, 11))

    # Crash three times in a row, two items at a time.
    for _ in range(3):
        with pytest.raises(SimulatedCrash):
            _run_until(path, items, crash_after=2)

    # Six items should be done by now; final run picks up the rest.
    assert JsonlStore(path).load_latest().completed_items == [1, 2, 3, 4, 5, 6]
    processed = _run_until(path, items, crash_after=None)
    assert processed == [7, 8, 9, 10]
