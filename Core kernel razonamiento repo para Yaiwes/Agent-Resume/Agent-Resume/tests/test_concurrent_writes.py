"""Tests for the thread-safety of the store layer."""

import threading

from agent_resume import Checkpoint, InMemoryStore, JsonlStore


def test_in_memory_store_handles_concurrent_appends():
    store = InMemoryStore()

    def worker(start: int) -> None:
        for i in range(start, start + 50):
            store.append(Checkpoint(turn=i, state={"i": i}))

    threads = [threading.Thread(target=worker, args=(t * 50,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(store) == 200


def test_jsonl_store_handles_concurrent_appends(tmp_path):
    store = JsonlStore(tmp_path / "race.ckpt", fsync=False)

    def worker(start: int) -> None:
        for i in range(start, start + 25):
            store.append(Checkpoint(turn=i, state={"i": i}))

    threads = [threading.Thread(target=worker, args=(t * 25,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All 100 lines should be intact and parseable.
    turns = sorted(c.turn for c in store.iter_checkpoints())
    assert turns == list(range(100))
