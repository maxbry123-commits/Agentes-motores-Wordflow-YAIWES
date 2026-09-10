"""The Worker base class: protected core + a single mutable method.

A *worker* is a single-responsibility agent. Each concrete worker declares four
things and nothing more:

* ``name`` — its identity in the pipeline.
* ``input_keys`` — the shared-state keys it reads (its input contract).
* ``output_key`` + ``output_schema`` — where it writes and the JSON shape it
  must produce (its output contract).
* ``default_instruction`` — the *mutable* part: free-text guidance describing
  how to do the job well.

The key architectural idea is the split between a **protected core** and a
**mutable method**:

* The **protected core** is the invariant protocol — input validation, system/
  prompt assembly, the call to the backend, output validation against the
  schema, and the write back into shared state. These methods are marked
  ``@final`` *and* a runtime guard rejects any subclass that tries to override
  them (see :meth:`Worker.__init_subclass__`). The protocol therefore cannot be
  broken by accident or by an automated tuning process.
* The **mutable method** is the instruction text, changed only through
  :meth:`Worker.propose_instruction`, which validates the candidate and bumps a
  version counter. The Manager's self-improvement loop is allowed to rewrite the
  instruction to raise quality, but because it can *only* touch this field, it
  can never change what the worker reads, what it writes, or the shape of that
  output. Tuning can make a worker better; it can never make it break the
  pipeline.
"""

from __future__ import annotations

import json
import time
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Tuple, final

from .errors import ContractViolation, ProtectedCoreError
from .llm import LLMBackend
from .state import SharedState

MAX_INSTRUCTION_CHARS = 4000

#: The invariant protocol injected into every worker's system prompt. It frames
#: the worker as single-responsibility and pins down the JSON-only output rule.
PROTOCOL_RULES = (
    "You are a single-responsibility worker inside an automated pipeline.\n"
    "- Use ONLY the data provided under [INPUTS]. Do not invent facts.\n"
    "- Perform exactly the job described under [TASK]; never do adjacent work.\n"
    "- Respond with ONE JSON object that satisfies [OUTPUT CONTRACT].\n"
    "- Emit no prose, preamble, or commentary outside that JSON object."
)

# Methods that constitute the protected core. A subclass that defines any of
# these in its own body is rejected at class-creation time.
_PROTECTED_METHODS = frozenset(
    {
        "run",
        "render_prompt",
        "build_system",
        "propose_instruction",
        "instruction_state",
        "restore_instruction",
        "_validate_output",
    }
)


@dataclass
class WorkerResult:
    """The outcome of one worker invocation."""

    worker: str
    output: Any
    raw_text: str
    instruction_version: int
    usage: Dict[str, Any] = field(default_factory=dict)
    elapsed_s: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker": self.worker,
            "output": self.output,
            "raw_text": self.raw_text,
            "instruction_version": self.instruction_version,
            "usage": self.usage,
            "elapsed_s": self.elapsed_s,
        }


class Worker(ABC):
    """Base class for all workers. Subclass it; do not override its core."""

    # --- subclass-declared configuration (override these) -----------------
    name: ClassVar[str] = ""
    persona: ClassVar[str] = "a meticulous specialist"
    input_keys: ClassVar[Tuple[str, ...]] = ()
    output_key: ClassVar[str] = ""
    output_schema: ClassVar[Dict[str, Any]] = {}
    default_instruction: ClassVar[str] = ""

    # --- protected-core enforcement --------------------------------------
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        overridden = [m for m in _PROTECTED_METHODS if m in cls.__dict__]
        if overridden:
            raise ProtectedCoreError(
                f"{cls.__name__} may not override protected-core method(s): "
                f"{', '.join(sorted(overridden))}. Tune behavior through "
                f"'default_instruction' / propose_instruction() instead."
            )

    def __init__(self, instruction: Optional[str] = None) -> None:
        self._require_class_config()
        self._instruction: str = (instruction or self.default_instruction).strip()
        self._instruction_version: int = 0
        self._instruction_history: List[str] = [self._instruction]

    def _require_class_config(self) -> None:
        missing = [
            attr
            for attr in ("name", "output_key", "default_instruction")
            if not getattr(self, attr)
        ]
        if missing:
            raise ProtectedCoreError(
                f"{type(self).__name__} must define class attribute(s): "
                f"{', '.join(missing)}"
            )

    # --- the single mutable surface --------------------------------------
    @property
    def instruction(self) -> str:
        """The current (mutable) task instruction."""
        return self._instruction

    @property
    def instruction_version(self) -> int:
        """How many times the instruction has been successfully changed."""
        return self._instruction_version

    @final
    def propose_instruction(self, new_instruction: str) -> bool:
        """Attempt to replace the mutable instruction.

        Returns ``True`` if accepted (and bumps the version), ``False`` if the
        candidate is empty, too long, the wrong type, or unchanged. This is the
        *only* sanctioned way to mutate a worker, and it cannot touch the I/O
        contract — that lives in the protected core.
        """
        if not isinstance(new_instruction, str):
            return False
        candidate = new_instruction.strip()
        if not candidate or len(candidate) > MAX_INSTRUCTION_CHARS:
            return False
        if candidate == self._instruction:
            return False
        self._instruction = candidate
        self._instruction_version += 1
        self._instruction_history.append(candidate)
        return True

    @final
    def instruction_state(self) -> Dict[str, Any]:
        """Serialize the mutable state (for checkpointing)."""
        return {
            "instruction": self._instruction,
            "version": self._instruction_version,
            "history": list(self._instruction_history),
        }

    @final
    def restore_instruction(self, snapshot: Dict[str, Any]) -> None:
        """Restore mutable state from a checkpoint snapshot."""
        self._instruction = snapshot["instruction"]
        self._instruction_version = int(snapshot.get("version", 0))
        self._instruction_history = list(
            snapshot.get("history", [self._instruction])
        )

    # --- the protected core ----------------------------------------------
    @final
    def build_system(self) -> str:
        """Assemble the immutable system prompt (persona + protocol)."""
        return (
            f"You are {self.persona}, acting as the '{self.name}' worker.\n\n"
            f"[PROTOCOL]\n{PROTOCOL_RULES}"
        )

    @final
    def render_prompt(self, state: SharedState) -> str:
        """Assemble the user prompt from the mutable task + inputs + contract.

        The mutable instruction is placed under ``[TASK]``, but the framework —
        not the instruction — owns the ``[INPUTS]`` rendering and the
        ``[OUTPUT CONTRACT]`` schema. That is what makes a bad instruction unable
        to break the protocol.
        """
        inputs = {key: state.require(key) for key in self.input_keys}
        return "\n".join(
            [
                "[TASK]",
                self._instruction,
                "",
                "[INPUTS]",
                json.dumps(inputs, indent=2, ensure_ascii=False, default=str),
                "",
                "[OUTPUT CONTRACT]",
                "Return exactly one JSON object matching this JSON Schema:",
                json.dumps(self.output_schema, indent=2, ensure_ascii=False),
            ]
        )

    @final
    def _validate_output(self, data: Any) -> Dict[str, Any]:
        """Enforce the output contract: object type + required keys present."""
        if not isinstance(data, dict):
            raise ContractViolation(
                f"{self.name}: expected a JSON object, got "
                f"{type(data).__name__}"
            )
        required = []
        if isinstance(self.output_schema, dict):
            required = self.output_schema.get("required", []) or []
        missing = [key for key in required if key not in data]
        if missing:
            raise ContractViolation(
                f"{self.name}: output is missing required key(s): "
                f"{', '.join(missing)}"
            )
        return data

    @final
    def run(
        self,
        state: SharedState,
        backend: LLMBackend,
        *,
        context_extra: Optional[Dict[str, Any]] = None,
    ) -> WorkerResult:
        """Execute the worker once.

        This is the invariant pipeline step:
        validate inputs -> build prompt -> call backend -> validate output ->
        write to shared state. None of it can be overridden by a subclass.
        """
        start = time.perf_counter()
        system = self.build_system()
        prompt = self.render_prompt(state)  # raises if an input is missing

        context: Dict[str, Any] = {
            "worker": self.name,
            "purpose": "worker",
            "instruction_version": self._instruction_version,
        }
        if context_extra:
            context.update(context_extra)

        response = backend.generate(
            system=system,
            prompt=prompt,
            schema=self.output_schema or None,
            context=context,
        )

        data = response.data
        if data is None:
            # Backend returned raw text only; parse it ourselves.
            try:
                data = json.loads(response.text)
            except (json.JSONDecodeError, TypeError) as exc:
                raise ContractViolation(
                    f"{self.name}: response was not valid JSON: {exc}"
                ) from exc

        output = self._validate_output(data)
        state.set(self.output_key, output)

        return WorkerResult(
            worker=self.name,
            output=output,
            raw_text=response.text,
            instruction_version=self._instruction_version,
            usage=response.usage,
            elapsed_s=time.perf_counter() - start,
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"instruction_version={self._instruction_version})"
        )
