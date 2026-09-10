"""Stage 7.3 — local coding of individual segments.

For each segment produces a CodedSegment with core fields (quote, subject_codes,
content_type, research_question_ids, hypothesis_support, respondent meta, screen_state)
and the non-core interpretive_notes field.

Key design:
  - Each segment is coded in isolation except for a small recent-context window.
  - Global interview context is passed to every call (small, cheap).
  - Project codebook is passed so the model can reuse canonical codes.
  - Vision enrichment is conditional: only if the config says so AND the segment contains
    at least one trigger word AND the segment has screen_state from stage 6.2.
  - Citation validation: we check that the quote appears in the transcript (normalized or
    fuzzy match per config). If not, retry up to max_retries times.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from backends import LLMBackend
from backends.base import LLMMessage
from schemas import (
    Brief,
    CodedSegment,
    CodedSegmentMeta,
    GlobalContext,
    ProjectCodebook,
    RawTranscript,
    Respondent,
    ScreenStateRef,
    Segment,
)
from .validation import quote_matches_transcript

logger = logging.getLogger(__name__)


CODED_SEGMENT_SCHEMA: dict[str, Any] = {
    "title": "CodedSegment",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "quote",
        "quote_cleaned",
        "subject_codes",
        "content_type",
        "research_question_ids",
        "hypothesis_support",
        "screen_state",
        "interpretive_notes",
    ],
    "properties": {
        "quote": {"type": "string"},
        "quote_cleaned": {"type": ["string", "null"]},
        "subject_codes": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 5,
        },
        "content_type": {
            "type": "string",
            "enum": ["insight", "problem", "wish", "action", "state", "process"],
        },
        "research_question_ids": {
            "type": "array",
            "items": {"type": "string"},
        },
        "hypothesis_support": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["hypothesis_id", "direction", "note"],
                "properties": {
                    "hypothesis_id": {"type": "string"},
                    "direction": {
                        "type": "string",
                        "enum": ["for", "against", "mixed", "none"],
                    },
                    "note": {"type": ["string", "null"]},
                },
            },
        },
        "screen_state": {
            "anyOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["screenshot_ref", "description"],
                    "properties": {
                        "screenshot_ref": {"type": ["string", "null"]},
                        "description": {"type": "string"},
                    },
                },
            ]
        },
        "interpretive_notes": {"type": ["string", "null"]},
    },
}


def _should_trigger_vision(segment_text: str, trigger_words: list[str]) -> bool:
    lower = segment_text.lower()
    return any(w.lower() in lower for w in trigger_words)


def _build_screen_state_block(
    segment_utterances: list[dict[str, Any]],
    vision_mode: str,
    trigger_words: list[str],
) -> tuple[str, list[bytes]]:
    """Return (textual block describing screen state, list of image bytes to pass)."""
    # Collect screen states from utterances that have them.
    screens = [u.get("screen_state") for u in segment_utterances if u.get("screen_state")]
    if not screens:
        return "", []

    # Textual description is always included.
    descs = [s["description"] for s in screens if s.get("description")]
    text_block = "### Screen state during this segment\n\n" + "\n".join(
        f"- {d}" for d in descs
    ) if descs else ""

    if vision_mode == "never":
        return text_block, []

    # For "always" or "triggered" mode, load image bytes if a screenshot_ref points to a file.
    segment_text = " ".join(u.get("text", "") for u in segment_utterances)
    should_load_images = (
        vision_mode == "always"
        or (vision_mode == "triggered" and _should_trigger_vision(segment_text, trigger_words))
    )
    if not should_load_images:
        return text_block, []

    images: list[bytes] = []
    for s in screens:
        ref = s.get("screenshot_ref")
        if ref and Path(ref).exists():
            try:
                images.append(Path(ref).read_bytes())
            except OSError as e:
                logger.warning("Could not read screenshot %s: %s", ref, e)
    return text_block, images


def code_segments(
    transcript: RawTranscript,
    segments: list[Segment],
    global_context: GlobalContext,
    brief: Brief,
    respondent: Respondent,
    codebook: ProjectCodebook,
    *,
    backend: LLMBackend,
    model: str,
    prompt_system_template: str,
    prompt_user_template: str,
    interpretive_frames: str,
    prompt_version: str,
    reasoning_effort: str = "medium",
    max_tokens: int = 4000,
    context_window_size: int = 3,
    max_retries: int = 3,
    vision_mode: str = "triggered",
    trigger_words: Optional[list[str]] = None,
    citation_match_mode: str = "normalized",
    fuzzy_threshold: float = 0.92,
    on_citation_mismatch: str = "retry",
    checkpoint_path: Optional[Path] = None,
) -> list[CodedSegment]:
    """Code all segments sequentially. Writes a checkpoint file after each segment if
    checkpoint_path is given."""
    trigger_words = trigger_words or []
    coded: list[CodedSegment] = []
    transcript_full_text = transcript.full_text()

    # Resume from checkpoint if present.
    if checkpoint_path is not None and checkpoint_path.exists():
        try:
            existing = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            coded = [CodedSegment(**c) for c in existing]
            logger.info("Resumed from checkpoint: %d segments already coded", len(coded))
        except Exception as e:
            logger.warning("Could not resume from checkpoint: %s. Starting fresh.", e)
            coded = []

    done_ids = {c.segment_id for c in coded}

    # Pre-render the system prompt once (it doesn't depend on segment).
    system_prompt = prompt_system_template.replace("{interpretive_frames}", interpretive_frames)
    system_prompt = system_prompt.replace("{context_window_size}", str(context_window_size))

    for i, seg in enumerate(segments):
        if seg.segment_id in done_ids:
            continue

        # Build utterance list for this segment.
        seg_utterances = [
            {
                "speaker": transcript.utterances[idx].speaker,
                "text": transcript.utterances[idx].text,
                "start": transcript.utterances[idx].start,
                "end": transcript.utterances[idx].end,
                "screen_state": (
                    transcript.utterances[idx].screen_state.model_dump()
                    if transcript.utterances[idx].screen_state
                    else None
                ),
            }
            for idx in seg.utterance_indices
        ]

        # Screen state block (text + optional images).
        screen_state_block, images = _build_screen_state_block(
            seg_utterances, vision_mode, trigger_words
        )

        # Recent context: last N coded segments.
        recent = coded[-context_window_size:] if coded else []
        recent_payload = [
            {
                "segment_id": c.segment_id,
                "timecode_start": c.timecode_start,
                "quote": c.quote,
                "subject_codes": c.subject_codes,
                "content_type": c.content_type,
            }
            for c in recent
        ]

        user_prompt = prompt_user_template.format(
            global_context_json=json.dumps(global_context.model_dump(), ensure_ascii=False, indent=2),
            respondent_json=json.dumps(respondent.model_dump(), ensure_ascii=False, indent=2),
            research_questions_json=json.dumps(
                [rq.model_dump() for rq in brief.research_questions], ensure_ascii=False, indent=2
            ),
            hypotheses_json=json.dumps(
                [h.model_dump() for h in brief.hypotheses], ensure_ascii=False, indent=2
            ),
            codebook_json=json.dumps(
                [e.model_dump() for e in codebook.entries], ensure_ascii=False, indent=2
            ),
            recent_count=len(recent_payload),
            recent_segments_json=json.dumps(recent_payload, ensure_ascii=False, indent=2),
            segment_id=seg.segment_id,
            interview_id=transcript.interview_id,
            timecode_start=seg.timecode_start,
            timecode_end=seg.timecode_end,
            guide_block=seg.guide_block or "null",
            segment_utterances_json=json.dumps(seg_utterances, ensure_ascii=False, indent=2),
            screen_state_block=screen_state_block,
        )

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt, images=images),
        ]

        logger.info("Coding segment %d/%d (%s)", i + 1, len(segments), seg.segment_id)

        last_err: str = ""
        retries = 0
        warnings: list[str] = []
        parsed: Optional[dict[str, Any]] = None

        for attempt in range(max_retries + 1):
            resp = backend.complete(
                messages=messages,
                model=model,
                response_schema=CODED_SEGMENT_SCHEMA,
                reasoning_effort=reasoning_effort,
                max_tokens=max_tokens,
            )
            if resp.parsed is None:
                last_err = f"Unparseable JSON (attempt {attempt + 1})"
                logger.warning("%s; retrying", last_err)
                retries += 1
                continue

            # Citation check.
            quote = resp.parsed.get("quote", "")
            if not quote_matches_transcript(
                quote, transcript_full_text, mode=citation_match_mode, fuzzy_threshold=fuzzy_threshold
            ):
                if on_citation_mismatch == "retry" and attempt < max_retries:
                    last_err = "Citation mismatch"
                    logger.warning(
                        "Segment %s: quote not found in transcript (attempt %d). Retrying.",
                        seg.segment_id, attempt + 1,
                    )
                    # Append a corrective message for next attempt.
                    messages = list(messages) + [
                        LLMMessage(role="assistant", content=json.dumps(resp.parsed, ensure_ascii=False)),
                        LLMMessage(
                            role="user",
                            content=(
                                f"The quote you produced does not appear verbatim in the transcript. "
                                f"The quote must match the source text exactly (normalization of whitespace "
                                f"and punctuation is allowed). Regenerate the JSON with a correct quote."
                            ),
                        ),
                    ]
                    retries += 1
                    continue
                elif on_citation_mismatch == "warn":
                    warnings.append("Citation does not match transcript verbatim")
                elif on_citation_mismatch == "fail":
                    raise RuntimeError(
                        f"Segment {seg.segment_id}: citation mismatch. Quote: {quote!r}"
                    )

            parsed = resp.parsed
            break
        else:
            # All retries exhausted
            warnings.append(f"Failed after {max_retries} retries: {last_err}")
            parsed = resp.parsed or {}

        if parsed is None:
            logger.error("Segment %s: no parseable output after retries; skipping", seg.segment_id)
            continue

        # Build the CodedSegment Pydantic object.
        screen_state_obj = None
        if parsed.get("screen_state"):
            screen_state_obj = ScreenStateRef(**parsed["screen_state"])

        coded_segment = CodedSegment(
            segment_id=seg.segment_id,
            interview_id=transcript.interview_id,
            timecode_start=seg.timecode_start,
            timecode_end=seg.timecode_end,
            guide_block=seg.guide_block,
            quote=parsed["quote"],
            quote_cleaned=parsed.get("quote_cleaned"),
            subject_codes=parsed["subject_codes"],
            content_type=parsed["content_type"],
            research_question_ids=parsed["research_question_ids"],
            hypothesis_support=parsed.get("hypothesis_support", []),
            respondent_id=respondent.id,
            respondent_segment=respondent.segment,
            respondent_city=respondent.city,
            screen_state=screen_state_obj,
            interpretive_notes=parsed.get("interpretive_notes"),
            meta=CodedSegmentMeta(
                model=resp.model or model,
                prompt_version=prompt_version,
                retries=retries,
                validation_warnings=warnings,
            ),
        )
        coded.append(coded_segment)

        # Checkpoint after each segment.
        if checkpoint_path is not None:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint_path.write_text(
                json.dumps([c.model_dump() for c in coded], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    logger.info("Local coding done: %d segments coded", len(coded))
    return coded
