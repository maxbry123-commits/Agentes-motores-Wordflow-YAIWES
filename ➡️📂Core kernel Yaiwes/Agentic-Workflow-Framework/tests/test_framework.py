"""Test suite for the agentic_workflow framework.

These tests run fully offline against ``MockLLMBackend`` — no API key, no
network. They cover the shared state contract, the protected-core guarantee, the
worker run protocol, checkpoint round-trips, end-to-end orchestration, clean
stop/resume, and the self-improvement loop.

Run with ``pytest`` (or ``python -m pytest``) from the project root.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_workflow import (
    CheckpointStore,
    ContractViolation,
    EvalResult,
    Manager,
    MockLLMBackend,
    Pipeline,
    ProtectedCoreError,
    SharedState,
    Step,
    Worker,
)


# --------------------------------------------------------------------------- #
# Minimal workers used across tests                                           #
# --------------------------------------------------------------------------- #
class UpperWorker(Worker):
    name = "upper"
    input_keys = ("text",)
    output_key = "loud"
    output_schema = {
        "type": "object",
        "properties": {"loud": {"type": "string"}},
        "required": ["loud"],
        "additionalProperties": False,
    }
    default_instruction = "Uppercase the text."


class EchoWorker(Worker):
    name = "echo"
    input_keys = ("loud",)
    output_key = "echo"
    output_schema = {
        "type": "object",
        "properties": {"echo": {"type": "string"}},
        "required": ["echo"],
        "additionalProperties": False,
    }
    default_instruction = "Echo the input."


def make_backend() -> MockLLMBackend:
    backend = MockLLMBackend()
    backend.register("upper", lambda i, c, p: {"loud": "HELLO"})
    backend.register("echo", lambda i, c, p: {"echo": "HELLO"})
    return backend


# --------------------------------------------------------------------------- #
# SharedState                                                                  #
# --------------------------------------------------------------------------- #
def test_shared_state_require_raises_on_missing_key():
    state = SharedState()
    with pytest.raises(ContractViolation):
        state.require("missing")


def test_shared_state_set_bumps_revision_and_roundtrips():
    state = SharedState()
    assert state.revision == 0
    state.set("a", 1)
    assert state.revision == 1
    assert state.require("a") == 1

    restored = SharedState.from_dict(state.to_dict())
    assert restored.require("a") == 1
    assert restored.revision == state.revision


# --------------------------------------------------------------------------- #
# Protected core enforcement                                                   #
# --------------------------------------------------------------------------- #
def test_overriding_protected_method_is_rejected():
    with pytest.raises(ProtectedCoreError):

        class Bad(Worker):  # noqa: D401 - intentional contract violation
            name = "bad"
            output_key = "x"
            default_instruction = "do"

            def run(self, *args, **kwargs):  # type: ignore[override]
                return None


def test_missing_class_config_is_rejected_at_init():
    class Incomplete(Worker):
        name = "incomplete"
        # no output_key / default_instruction

    with pytest.raises(ProtectedCoreError):
        Incomplete()


def test_propose_instruction_validates_and_versions():
    worker = UpperWorker()
    assert worker.instruction_version == 0

    assert worker.propose_instruction("Shout the text loudly.") is True
    assert worker.instruction_version == 1
    assert "loudly" in worker.instruction

    # Empty, unchanged, and over-long candidates are all rejected.
    assert worker.propose_instruction("   ") is False
    assert worker.propose_instruction(worker.instruction) is False
    assert worker.propose_instruction("x" * 5000) is False
    assert worker.instruction_version == 1


# --------------------------------------------------------------------------- #
# Worker run protocol                                                          #
# --------------------------------------------------------------------------- #
def test_worker_run_validates_output_and_writes_state():
    state = SharedState({"text": "hello"})
    result = UpperWorker().run(state, make_backend())
    assert result.output == {"loud": "HELLO"}
    assert state.require("loud") == {"loud": "HELLO"}


def test_worker_run_missing_input_raises_contract_violation():
    state = SharedState()  # no "text"
    with pytest.raises(ContractViolation):
        UpperWorker().run(state, make_backend())


def test_worker_run_missing_required_output_key_raises():
    backend = MockLLMBackend()
    backend.register("upper", lambda i, c, p: {"wrong": "value"})
    state = SharedState({"text": "hi"})
    with pytest.raises(ContractViolation):
        UpperWorker().run(state, backend)


# --------------------------------------------------------------------------- #
# Checkpoint store                                                             #
# --------------------------------------------------------------------------- #
def test_checkpoint_roundtrip(tmp_path: Path):
    store = CheckpointStore(tmp_path / "ckpt")
    payload = {"cursor": 2, "state": {"data": {"k": "v"}}}
    store.save("run1", payload)
    assert store.exists("run1")
    assert store.load("run1")["cursor"] == 2
    assert store.list() == ["run1"]
    assert store.latest() == "run1"


# --------------------------------------------------------------------------- #
# Manager: end-to-end, stop/resume                                            #
# --------------------------------------------------------------------------- #
def test_manager_runs_pipeline_to_completion():
    pipeline = Pipeline([Step(UpperWorker()), Step(EchoWorker())])
    manager = Manager(pipeline, make_backend(), state=SharedState({"text": "hi"}))
    state = manager.run()
    assert manager.is_done
    assert state.require("echo") == {"echo": "HELLO"}
    assert len(state.history) == 2


def test_manager_stop_and_resume(tmp_path: Path):
    store = CheckpointStore(tmp_path / "ckpt")
    pipeline = Pipeline([Step(UpperWorker()), Step(EchoWorker())])
    manager = Manager(
        pipeline,
        make_backend(),
        state=SharedState({"text": "hi"}),
        checkpoint_store=store,
        run_id="r",
    )

    manager.run(max_steps=1)
    assert manager.cursor == 1
    assert not manager.is_done

    # Fresh pipeline + backend, restored purely from disk.
    fresh = Pipeline([Step(UpperWorker()), Step(EchoWorker())])
    resumed = Manager.resume(fresh, make_backend(), store, "r")
    assert resumed.cursor == 1
    resumed.run()
    assert resumed.is_done
    assert resumed.state.require("echo") == {"echo": "HELLO"}


def test_resume_rejects_mismatched_pipeline(tmp_path: Path):
    store = CheckpointStore(tmp_path / "ckpt")
    pipeline = Pipeline([Step(UpperWorker()), Step(EchoWorker())])
    manager = Manager(
        pipeline, make_backend(), checkpoint_store=store, run_id="r",
        state=SharedState({"text": "hi"}),
    )
    manager.checkpoint()

    wrong = Pipeline([Step(UpperWorker())])  # different shape
    from agentic_workflow import CheckpointError

    with pytest.raises(CheckpointError):
        Manager.resume(wrong, make_backend(), store, "r")


# --------------------------------------------------------------------------- #
# Self-improvement loop                                                        #
# --------------------------------------------------------------------------- #
class DraftWorker(Worker):
    name = "draft"
    input_keys = ("topic",)
    output_key = "draft"
    output_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
        "additionalProperties": False,
    }
    default_instruction = "Write something."


def length_evaluator(result, state) -> EvalResult:
    text = str(result.output.get("text", ""))
    return EvalResult(score=1.0 if len(text) >= 50 else 0.0, feedback="Make it longer.")


def test_self_improvement_raises_score_without_touching_core():
    backend = MockLLMBackend()
    # First draft too short; improved draft long enough.
    backend.register(
        "draft",
        lambda i, c, p: {"text": "short" if i == 0 else "x" * 80},
    )
    backend.register(
        "draft",
        lambda i, c, p: {"improved_instruction": "Write at least 50 characters."},
        purpose="improvement",
    )

    pipeline = Pipeline(
        [Step(DraftWorker(), evaluator=length_evaluator, improve_threshold=1.0)]
    )
    manager = Manager(
        pipeline, backend, state=SharedState({"topic": "cats"}),
        max_improvement_rounds=2,
    )
    manager.run()

    worker = pipeline.worker_by_name("draft")
    # The mutable instruction changed (version bumped) ...
    assert worker.instruction_version == 1
    # ... and the kept output is the improved, longer one.
    assert len(manager.state.require("draft")["text"]) >= 50
    # ... and there is an improvement-round entry in the log.
    assert any(e["event"] == "improvement_round" for e in manager.log)
