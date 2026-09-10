"""Stage 7.2 — global interview context."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backends import LLMBackend
from backends.base import LLMMessage
from schemas import Brief, GlobalContext, RawTranscript

logger = logging.getLogger(__name__)


GLOBAL_CONTEXT_SCHEMA: dict[str, Any] = {
    "title": "GlobalContext",
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "themes", "participants", "key_tasks", "notable_dynamics"],
    "properties": {
        "summary": {"type": "string"},
        "themes": {"type": "array", "items": {"type": "string"}},
        "participants": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "key_tasks": {"type": "array", "items": {"type": "string"}},
        "notable_dynamics": {"type": ["string", "null"]},
    },
}


def build_global_context(
    transcript: RawTranscript,
    brief: Brief,
    *,
    backend: LLMBackend,
    model: str,
    prompt_system: str,
    prompt_user: str,
    reasoning_effort: str = "medium",
    max_tokens: int = 3000,
) -> GlobalContext:
    transcript_text = [
        {"speaker": u.speaker, "text": u.text} for u in transcript.utterances
    ]
    rendered_user = prompt_user.format(
        brief_json=json.dumps(brief.model_dump(), ensure_ascii=False, indent=2),
        transcript_json=json.dumps(transcript_text, ensure_ascii=False, indent=2),
    )
    messages = [
        LLMMessage(role="system", content=prompt_system),
        LLMMessage(role="user", content=rendered_user),
    ]

    logger.info("Global pass: calling %s", model)
    resp = backend.complete(
        messages=messages,
        model=model,
        response_schema=GLOBAL_CONTEXT_SCHEMA,
        reasoning_effort=reasoning_effort,
        max_tokens=max_tokens,
    )
    if resp.parsed is None:
        raise RuntimeError(
            "Global pass failed: model did not return parseable JSON. "
            f"Raw text:\n{resp.text[:500]}"
        )
    return GlobalContext(**resp.parsed)


def save_global_context(ctx: GlobalContext, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ctx.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_global_context(path: Path) -> GlobalContext:
    return GlobalContext(**json.loads(path.read_text(encoding="utf-8")))
