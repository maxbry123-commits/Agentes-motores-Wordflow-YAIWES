"""Stage 7.1 — segmentation.

Takes a raw transcript (list of short utterances produced by STT + diarization) and
groups them into coherent semantic segments of 30–90 seconds each.

For very long transcripts that exceed a reasonable single-call budget, we fall back to a
chunked pass with overlap. In practice GPT-5.4's 1.05M context window handles interviews
under ~2 hours without chunking.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backends import LLMBackend
from schemas import RawTranscript, Segment

logger = logging.getLogger(__name__)


SEGMENTATION_SCHEMA: dict[str, Any] = {
    "title": "Segmentation",
    "type": "object",
    "additionalProperties": False,
    "required": ["segments"],
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "segment_id",
                    "timecode_start",
                    "timecode_end",
                    "draft_title",
                    "utterance_indices",
                    "guide_block",
                ],
                "properties": {
                    "segment_id": {"type": "string"},
                    "timecode_start": {"type": "number"},
                    "timecode_end": {"type": "number"},
                    "draft_title": {"type": "string"},
                    "utterance_indices": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                    },
                    "guide_block": {"type": ["string", "null"]},
                },
            },
        },
    },
}


def segment_transcript(
    transcript: RawTranscript,
    *,
    backend: LLMBackend,
    model: str,
    prompt_system: str,
    prompt_user: str,
    reasoning_effort: str = "low",
    max_tokens: int = 4000,
    target_duration: int = 45,
    max_duration: int = 120,
    min_duration: int = 15,
) -> list[Segment]:
    """Run the segmentation LLM call and return a list of Segment objects."""
    total_duration = transcript.utterances[-1].end if transcript.utterances else 0
    transcript_for_prompt = [
        {
            "idx": i,
            "start": u.start,
            "end": u.end,
            "speaker": u.speaker,
            "text": u.text,
        }
        for i, u in enumerate(transcript.utterances)
    ]

    rendered_user = prompt_user.format(
        total_utterances=len(transcript.utterances),
        total_duration=round(total_duration, 1),
        transcript_json=json.dumps(transcript_for_prompt, ensure_ascii=False, indent=2),
    )
    rendered_system = prompt_system.format(
        target_duration=target_duration,
        max_duration=max_duration,
        min_duration=min_duration,
    )

    from backends.base import LLMMessage
    messages = [
        LLMMessage(role="system", content=rendered_system),
        LLMMessage(role="user", content=rendered_user),
    ]

    logger.info("Segmentation: calling %s (%d utterances, ~%ds)",
                model, len(transcript.utterances), int(total_duration))
    resp = backend.complete(
        messages=messages,
        model=model,
        response_schema=SEGMENTATION_SCHEMA,
        reasoning_effort=reasoning_effort,
        max_tokens=max_tokens,
    )

    if resp.parsed is None:
        raise RuntimeError(
            "Segmentation failed: model did not return parseable JSON. "
            f"Raw text:\n{resp.text[:500]}"
        )

    segments = [Segment(**s) for s in resp.parsed["segments"]]
    logger.info("Segmentation: got %d segments (avg %ds each)",
                len(segments),
                int(total_duration / max(len(segments), 1)))
    return segments


def save_segments(segments: list[Segment], path: Path) -> None:
    """Persist segments to JSON for checkpointing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [s.model_dump() for s in segments]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_segments(path: Path) -> list[Segment]:
    """Load segments from a checkpoint file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Segment(**s) for s in data]
