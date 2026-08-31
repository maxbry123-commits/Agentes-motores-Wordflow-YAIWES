"""Tests for resume_or_start() in the fresh-run case."""

from agent_resume import InMemoryStore, resume_or_start


def test_fresh_start_yields_all_items():
    store = InMemoryStore()
    run = resume_or_start(
        store=store,
        initial_state={"processed": []},
        work_items=[1, 2, 3, 4, 5],
    )
    assert not run.resumed
    assert run.state == {"processed": []}

    seen = []
    for item in run:
        seen.append(item)
        run.checkpoint({"processed": seen.copy()})

    assert seen == [1, 2, 3, 4, 5]
    assert len(store) == 5


def test_fresh_start_initial_state_is_copied():
    initial = {"counter": 0}
    store = InMemoryStore()
    run = resume_or_start(store=store, initial_state=initial, work_items=[])
    run.state["counter"] = 42
    # Mutation through .state should NOT leak back into the caller's dict.
    assert initial == {"counter": 0}


def test_fresh_start_no_items_iterates_zero_times():
    store = InMemoryStore()
    run = resume_or_start(store=store, work_items=[])
    seen = list(run)
    assert seen == []
    assert run.turn == 0


def test_item_key_function_used_for_dedup():
    store = InMemoryStore()
    items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    run = resume_or_start(
        store=store,
        work_items=items,
        item_key=lambda x: x["id"],
    )
    for item in run:
        run.checkpoint()
    assert run.completed_items == ["a", "b", "c"]
