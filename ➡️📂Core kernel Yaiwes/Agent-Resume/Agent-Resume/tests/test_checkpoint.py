"""Tests for the Checkpoint dataclass."""

import json
import time

import pytest

from agent_resume import Checkpoint


def test_checkpoint_defaults_timestamp_and_completed():
    before = time.time()
    ck = Checkpoint(turn=1, state={"x": 1})
    after = time.time()
    assert ck.completed_items == []
    assert before <= ck.timestamp <= after


def test_to_json_round_trip():
    ck = Checkpoint(turn=3, state={"x": 1, "y": "two"}, completed_items=[1, 2, 3])
    raw = ck.to_json()
    parsed = Checkpoint.from_json(raw)
    assert parsed.turn == 3
    assert parsed.state == {"x": 1, "y": "two"}
    assert parsed.completed_items == [1, 2, 3]


def test_to_json_is_single_line():
    ck = Checkpoint(turn=1, state={"msg": "hello world"})
    raw = ck.to_json()
    assert "\n" not in raw


def test_to_json_uses_default_for_non_serializable():
    # `default=str` should soft-handle weird types instead of crashing.
    from pathlib import Path
    ck = Checkpoint(turn=1, state={"path": Path("/tmp/x")})
    raw = ck.to_json()
    parsed = json.loads(raw)
    assert parsed["state"]["path"] == "/tmp/x"


def test_from_json_missing_state_defaults_to_empty():
    raw = json.dumps({"turn": 2, "timestamp": 123.0})
    ck = Checkpoint.from_json(raw)
    assert ck.state == {}
    assert ck.completed_items == []


def test_from_json_rejects_missing_turn():
    raw = json.dumps({"state": {}})
    with pytest.raises(KeyError):
        Checkpoint.from_json(raw)
