"""Tests for JsonlStore."""

import pytest

from agent_resume import Checkpoint, JsonlStore, NoCheckpoint


def test_load_latest_on_missing_file_raises_nocheckpoint(tmp_path):
    store = JsonlStore(tmp_path / "missing.ckpt")
    with pytest.raises(NoCheckpoint):
        store.load_latest()


def test_load_latest_on_empty_file_raises_nocheckpoint(tmp_path):
    path = tmp_path / "empty.ckpt"
    path.write_text("")
    store = JsonlStore(path)
    with pytest.raises(NoCheckpoint):
        store.load_latest()


def test_append_and_load_latest(tmp_path):
    store = JsonlStore(tmp_path / "run.ckpt")
    store.append(Checkpoint(turn=1, state={"a": 1}, completed_items=[1]))
    store.append(Checkpoint(turn=2, state={"a": 2}, completed_items=[1, 2]))

    latest = store.load_latest()
    assert latest.turn == 2
    assert latest.state == {"a": 2}
    assert latest.completed_items == [1, 2]


def test_iter_checkpoints_yields_in_order(tmp_path):
    store = JsonlStore(tmp_path / "run.ckpt")
    for i in range(1, 4):
        store.append(Checkpoint(turn=i, state={"i": i}))

    seen = [c.turn for c in store.iter_checkpoints()]
    assert seen == [1, 2, 3]


def test_iter_checkpoints_skips_blank_lines(tmp_path):
    path = tmp_path / "run.ckpt"
    store = JsonlStore(path)
    store.append(Checkpoint(turn=1, state={}))
    # Append a stray blank line. iter should ignore it.
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n\n")
    store.append(Checkpoint(turn=2, state={}))

    seen = [c.turn for c in store.iter_checkpoints()]
    assert seen == [1, 2]


def test_len_counts_checkpoints(tmp_path):
    store = JsonlStore(tmp_path / "run.ckpt")
    assert len(store) == 0
    for i in range(4):
        store.append(Checkpoint(turn=i, state={}))
    assert len(store) == 4


def test_creates_parent_dir(tmp_path):
    nested = tmp_path / "a" / "b" / "c" / "run.ckpt"
    store = JsonlStore(nested)
    store.append(Checkpoint(turn=1, state={}))
    assert nested.exists()


def test_fsync_off_still_writes(tmp_path):
    store = JsonlStore(tmp_path / "run.ckpt", fsync=False)
    store.append(Checkpoint(turn=1, state={"x": 1}))
    assert store.load_latest().turn == 1
