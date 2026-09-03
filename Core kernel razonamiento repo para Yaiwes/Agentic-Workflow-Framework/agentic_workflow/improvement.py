"""The self-improvement step: refine a worker's mutable instruction.

When a step's evaluator scores a worker output below the threshold, the Manager
asks the backend to rewrite that worker's *instruction* — and only its
instruction. The meta-prompt explicitly tells the model that the I/O contract is
fixed and off-limits, mirroring the protected-core guarantee in code.

The improved instruction is then handed back to :meth:`Worker.propose_instruction`,
which validates it before accepting. If the model returns something unusable, the
proposal is simply rejected and the worker keeps its previous instruction.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .llm import LLMBackend
from .pipeline import EvalResult
from .worker import PROTOCOL_RULES, Worker, WorkerResult

META_SYSTEM = (
    "You are a prompt engineer. You improve the TASK instruction of one worker "
    "in an automated pipeline so its outputs score higher against a rubric. "
    "You must preserve the worker's input/output contract exactly: never change "
    "which inputs it reads or the JSON shape it must produce. Improve only the "
    "guidance on HOW to do the job well."
)

#: The improvement call itself uses structured output so we can reliably read the
#: rewritten instruction back out.
INSTRUCTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "improved_instruction": {
            "type": "string",
            "description": "The rewritten TASK instruction for the worker.",
        }
    },
    "required": ["improved_instruction"],
    "additionalProperties": False,
}


def _build_meta_prompt(
    worker: Worker, result: WorkerResult, evaluation: EvalResult
) -> str:
    return "\n".join(
        [
            f"Worker name: {worker.name}",
            f"Worker reads inputs: {list(worker.input_keys)}",
            f"Worker writes output key: {worker.output_key}",
            "",
            "The worker operates under this fixed protocol (do NOT alter it):",
            PROTOCOL_RULES,
            "",
            "Output JSON schema the worker must satisfy (FIXED — do not change):",
            json.dumps(worker.output_schema, indent=2, ensure_ascii=False),
            "",
            "Current TASK instruction:",
            worker.instruction,
            "",
            "Most recent output produced with that instruction:",
            json.dumps(result.output, indent=2, ensure_ascii=False, default=str),
            "",
            f"Evaluator score: {evaluation.score:.2f} (target is higher).",
            f"Evaluator feedback: {evaluation.feedback or '(none)'}",
            "",
            "Rewrite the TASK instruction so the next output scores higher. "
            "Keep it concise and actionable. Address the feedback directly. "
            "Return JSON with a single 'improved_instruction' field.",
        ]
    )


def improve_instruction(
    backend: LLMBackend,
    worker: Worker,
    result: WorkerResult,
    evaluation: EvalResult,
) -> Optional[str]:
    """Ask the backend for a better instruction; return it, or ``None``.

    The returned string is a *candidate*. The Manager passes it to
    :meth:`Worker.propose_instruction`, which has the final say on whether it is
    accepted.
    """
    prompt = _build_meta_prompt(worker, result, evaluation)
    response = backend.generate(
        system=META_SYSTEM,
        prompt=prompt,
        schema=INSTRUCTION_SCHEMA,
        context={"worker": worker.name, "purpose": "improvement"},
    )
    data = response.data
    if data is None:
        try:
            data = json.loads(response.text)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(data, dict):
        return None
    improved = data.get("improved_instruction")
    return improved if isinstance(improved, str) and improved.strip() else None
