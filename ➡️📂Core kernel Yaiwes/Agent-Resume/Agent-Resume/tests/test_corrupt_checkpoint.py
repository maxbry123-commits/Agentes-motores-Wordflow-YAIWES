"""Tests for corrupt checkpoint handling."""

import pytest

from agent_resume import Checkpoint, CheckpointCorrupt, JsonlStore


def test_garbage_line_raises_checkpoint_corrupt(tmp_path):
    path = tmp_path / "run.ckpt"
    path.write_text("this is not json\n")
    store = JsonlStore(path)
    with pytest.raises(CheckpointCorrupt) as exc_info:
        store.load_latest()
    assert exc_info.value.line_number == 1


def test_partial_line_after_valid_rows_raises(tmp_path):
    path = tmp_path / "run.ckpt"
    store = JsonlStore(path)
    store.append(Checkpoint(turn=1, state={}))
    # Simulate a half-written line from a crash mid-flush.
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"turn": 2, "state": {')

    with pytest.raises(CheckpointCorrupt) as exc_info:
        list(store.iter_checkpoints())
    assert exc_info.value.line_number == 2


def test_missing_turn_field_raises(tmp_path):
    path = tmp_path / "run.ckpt"
    path.write_text('{"state": {}}\n')
    store = JsonlStore(path)
    with pytest.raises(CheckpointCorrupt):
        store.load_latest()


def test_corrupt_exception_chains_underlying_cause(tmp_path):
    path = tmp_path / "run.ckpt"
    path.write_text("{bad json\n")
    store = JsonlStore(path)
    with pytest.raises(CheckpointCorrupt) as exc_info:
        store.load_latest()
    # The underlying JSON error should be the chained cause.
    assert exc_info.value.__cause__ is not None
