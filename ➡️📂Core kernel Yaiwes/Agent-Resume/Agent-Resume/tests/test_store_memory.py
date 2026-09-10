"""Tests for InMemoryStore."""

import pytest

from agent_resume import Checkpoint, InMemoryStore, NoCheckpoint


def test_load_latest_raises_when_empty():
    store = InMemoryStore()
    with pytest.raises(NoCheckpoint):
        store.load_latest()


def test_append_then_load_latest_returns_last():
    store = InMemoryStore()
    store.append(Checkpoint(turn=1, state={"v": "a"}))
    store.append(Checkpoint(turn=2, state={"v": "b"}))
    latest = store.load_latest()
    assert latest.turn == 2
    assert latest.state == {"v": "b"}


def test_all_returns_independent_copy():
    store = InMemoryStore()
    store.append(Checkpoint(turn=1, state={}))
    rows = store.all()
    rows.clear()
    # Original store should not be affected by mutation of returned list.
    assert len(store) == 1


def test_len_tracks_writes():
    store = InMemoryStore()
    assert len(store) == 0
    for i in range(5):
        store.append(Checkpoint(turn=i, state={}))
    assert len(store) == 5
