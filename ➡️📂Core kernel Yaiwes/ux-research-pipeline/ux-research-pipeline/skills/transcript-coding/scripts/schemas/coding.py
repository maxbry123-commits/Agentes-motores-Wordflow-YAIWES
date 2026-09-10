"""Pydantic schemas for outputs of the coding pipeline."""
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


ContentType = Literal["insight", "problem", "wish", "action", "state", "process"]


# ---- Stage 7.1 output ----

class Segment(BaseModel):
    """Semantic block produced by segmentation. Groups one or more utterances."""
    segment_id: str = Field(..., description="Stable id within the interview, e.g. 'seg_0042'")
    timecode_start: float = Field(..., description="Seconds")
    timecode_end: float = Field(..., description="Seconds")
    draft_title: str = Field(..., description="Short title for what this segment is about (for humans)")
    utterance_indices: list[int] = Field(
        ...,
        description="0-based indices of utterances in the source transcript that belong to this segment",
    )
    guide_block: Optional[str] = Field(None, description="If annotation from 6.3 is available")


# ---- Stage 7.2 output ----

class GlobalContext(BaseModel):
    """Summary of the entire interview, produced by a single LLM pass."""
    summary: str = Field(..., description="5-10 sentences describing what this interview was about")
    themes: list[str] = Field(..., description="Main themes, 5-10 items")
    participants: dict[str, str] = Field(
        default_factory=dict,
        description="Map of speaker label to short role description",
    )
    key_tasks: list[str] = Field(
        default_factory=list,
        description="Key tasks/stimuli that were tested during the interview",
    )
    notable_dynamics: Optional[str] = Field(
        None,
        description="Free text about remarkable shifts, tensions, or through-lines across the interview",
    )


# ---- Stage 7.3 output ----

class HypothesisSupport(BaseModel):
    hypothesis_id: str
    direction: Literal["for", "against", "mixed", "none"]
    note: Optional[str] = Field(None, description="Short clarification, one sentence")


class CodedSegmentMeta(BaseModel):
    """Run metadata attached to each coded segment for debugging and regression."""
    model: str
    prompt_version: str
    retries: int = 0
    validation_warnings: list[str] = Field(default_factory=list)


class CodedSegment(BaseModel):
    """Fully coded segment. This is the main output row of the pipeline.

    Fields are split into two tiers:
      - Core (strict validation): quote, subject_codes, content_type, research_question_ids,
        hypothesis_support, respondent, screen_state (if present)
      - Non-core (soft validation): interpretive_notes
    """
    # Identity
    segment_id: str
    interview_id: str
    timecode_start: float
    timecode_end: float
    guide_block: Optional[str] = None

    # Core — the quote
    quote: str = Field(..., description="Verbatim quote from the transcript — must match exactly")
    quote_cleaned: Optional[str] = Field(
        None,
        description="Optional cleaned version (hesitations removed) for reports",
    )

    # Core — content codes
    subject_codes: list[str] = Field(
        default_factory=list,
        description="Flat content codes close to the respondent's wording (in vivo). No hierarchy.",
    )
    content_type: ContentType = Field(
        ...,
        description="Type of content: insight, problem, wish, action, state, process",
    )

    # Core — research-question mapping
    research_question_ids: list[str] = Field(
        default_factory=list,
        description="Research question ids this segment speaks to",
    )
    hypothesis_support: list[HypothesisSupport] = Field(default_factory=list)

    # Core — respondent meta (copied from brief, not extracted from transcript)
    respondent_id: str
    respondent_segment: Optional[str] = None
    respondent_city: Optional[str] = None

    # Core — screen state if available
    screen_state: Optional["ScreenStateRef"] = None

    # Non-core — interpretive notes (free text with soft validation)
    interpretive_notes: Optional[str] = Field(
        None,
        description=(
            "Free-text observations through hermeneutic lenses (speech acts, frames, metaphors, "
            "modalities, attributions, Shchedrovitsky knowledge types, critical incidents, etc.). "
            "May be empty if nothing notable."
        ),
    )

    # Run metadata
    meta: CodedSegmentMeta


class ScreenStateRef(BaseModel):
    """Reference to the screen state at this segment (mirrors input schema)."""
    screenshot_ref: Optional[str] = None
    description: str


class CodedTranscript(BaseModel):
    """Top-level output for one interview."""
    interview_id: str
    project_id: str
    global_context: GlobalContext
    segments: list[CodedSegment]
    prompt_versions: dict[str, str] = Field(
        default_factory=dict,
        description="Version of each prompt used (segmentation, global_pass, local_coding, ...)",
    )


# ---- Project codebook ----

class CodebookEntry(BaseModel):
    """One canonical code in the project codebook, accumulating across interviews."""
    canonical: str = Field(..., description="Canonical form of the code")
    variants: list[str] = Field(
        default_factory=list,
        description="Synonymous variants that have been encountered and merged into this canonical code",
    )
    definition: Optional[str] = Field(
        None,
        description="Short definition, one sentence. Optional — can be filled by researcher.",
    )
    first_seen_interview: Optional[str] = None
    occurrences: int = Field(0, description="Total number of segments using this code across the project")


class ProjectCodebook(BaseModel):
    """Accumulative project-wide codebook of canonical codes."""
    project_id: str
    entries: list[CodebookEntry] = Field(default_factory=list)

    def canonical_for(self, code: str) -> Optional[str]:
        """Return canonical form if this code (or a variant) is already in the book."""
        lc = code.strip().lower()
        for e in self.entries:
            if e.canonical.strip().lower() == lc:
                return e.canonical
            for v in e.variants:
                if v.strip().lower() == lc:
                    return e.canonical
        return None
