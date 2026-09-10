"""Tests for resume_or_start() in the resume case."""

from agent_resume import Checkpoint, InMemoryStore, JsonlStore, resume_or_start


def test_resume_picks_up_state_and_skips_done_items():
    store = InMemoryStore()
    # First run: process items 1 and 2.
    run = resume_or_start(
        store=store,
        initial_state={"results": {}},
        work_items=[1, 2, 3, 4, 5],
    )
    for item in run:
        results = dict(run.state["results"])
        results[item] = f"r{item}"
        run.checkpoint({"results": results})
        if item == 2:
            break  # simulate crash

    # Second run: same code, should pick up from item 3.
    run2 = resume_or_start(
        store=store,
        initial_state={"results": {}},
        work_items=[1, 2, 3, 4, 5],
    )
    assert run2.resumed
    assert run2.state == {"results": {1: "r1", 2: "r2"}}
    assert run2.remaining_items() == [3, 4, 5]

    seen = []
    for item in run2:
        seen.append(item)
        results = dict(run2.state["results"])
        results[item] = f"r{item}"
        run2.checkpoint({"results": results})

    assert seen == [3, 4, 5]
    assert run2.state["results"] == {1: "r1", 2: "r2", 3: "r3", 4: "r4", 5: "r5"}


def test_resume_with_jsonl_store_survives_process_boundary(tmp_path):
    path = tmp_path / "issues.ckpt"

    # "Process 1" writes a few checkpoints then we drop the reference.
    store1 = JsonlStore(path)
    run1 = resume_or_start(
        store=store1,
        initial_state={"done": []},
        work_items=["a", "b", "c", "d"],
    )
    for item in run1:
        done = run1.state["done"] + [item]
        run1.checkpoint({"done": done})
        if item == "b":
            break
    del run1, store1

    # "Process 2" reopens the same file.
    store2 = JsonlStore(path)
    run2 = resume_or_start(
        store=store2,
        initial_state={"done": []},
        work_items=["a", "b", "c", "d"],
    )
    assert run2.resumed
    assert run2.state == {"done": ["a", "b"]}
    seen = list(run2)
    assert seen == ["c", "d"]


def test_resume_when_all_items_already_done_yields_nothing():
    store = InMemoryStore()
    store.append(
        Checkpoint(
            turn=3,
            state={"final": True},
            completed_items=[1, 2, 3],
        )
    )
    run = resume_or_start(
        store=store,
        initial_state={"final": False},
        work_items=[1, 2, 3],
    )
    assert run.resumed
    assert run.state == {"final": True}
    assert list(run) == []
    assert run.remaining_items() == []


def test_resume_ignores_initial_state_when_checkpoint_exists():
    store = InMemoryStore()
    store.append(Checkpoint(turn=1, state={"stored": True}, completed_items=[]))
    run = resume_or_start(
        store=store,
        initial_state={"fresh": True},  # should be ignored
        work_items=[1],
    )
    assert run.state == {"stored": True}


def test_turn_counter_advances_on_each_checkpoint():
    store = InMemoryStore()
    run = resume_or_start(store=store, work_items=[1, 2, 3])
    assert run.turn == 0
    for i, item in enumerate(run, start=1):
        run.checkpoint({"i": i})
        assert run.turn == i
