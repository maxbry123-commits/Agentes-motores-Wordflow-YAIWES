"""Pydantic schemas for inputs: raw transcript and research brief."""
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ---- Raw transcript (output of ux-transcribe) ----

class TranscriptUtterance(BaseModel):
    """Single utterance in the raw transcript.

    Minimal contract based on ux-transcribe output:
      [{"start": 1.1, "end": 5.2, "speaker": "Interviewer" | "Respondent", "text": "..."}, ...]

    Optional fields (screen_state, guide_block) may appear when the transcript
    has been enriched at stage 6. We tolerate their absence.
    """
    start: float = Field(..., description="Start time in seconds (float)")
    end: float = Field(..., description="End time in seconds (float)")
    speaker: str = Field(..., description="Speaker role, typically 'Interviewer' or 'Respondent'")
    text: str = Field(..., description="Utterance text, verbatim")

    # Optional enrichments from stage 6
    screen_state: Optional["ScreenState"] = None
    guide_block: Optional[str] = Field(
        None,
        description="Guide block label (e.g. 'payment testing'), if stage 6.3 marked it",
    )


class ScreenState(BaseModel):
    """Optional screen enrichment produced by stage 6.2."""
    screenshot_ref: Optional[str] = Field(None, description="Path to screenshot file")
    description: str = Field(..., description="Text description of what is on screen at this moment")


class RawTranscript(BaseModel):
    """Container for the full transcript. Accepts a list of utterances."""
    interview_id: str
    utterances: list[TranscriptUtterance]

    @field_validator("utterances")
    @classmethod
    def non_empty(cls, v: list[TranscriptUtterance]) -> list[TranscriptUtterance]:
        if not v:
            raise ValueError("Transcript cannot be empty")
        return v

    def full_text(self) -> str:
        """Concatenated transcript text — used for citation validation."""
        return "\n".join(f"{u.speaker}: {u.text}" for u in self.utterances)


# ---- Research brief (output of stage 1.3) ----

class ResearchQuestion(BaseModel):
    id: str = Field(..., description="Short id like 'rq_1' for referencing from codes")
    question: str
    notes: Optional[str] = None


class Hypothesis(BaseModel):
    id: str = Field(..., description="Short id like 'h_1'")
    statement: str
    notes: Optional[str] = None


class Respondent(BaseModel):
    id: str = Field(..., description="Short id like 'r_1'")
    segment: Optional[str] = Field(None, description="Segment label from screener (e.g. 'active users')")
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal["m", "f", "other"]] = None
    notes: Optional[str] = None


class Brief(BaseModel):
    """Input research brief. Required for stage 7.3 (mapping to research questions)."""
    project_id: str = Field(..., description="Project identifier, e.g. 'TICKET-123'")
    project_name: Optional[str] = None
    research_questions: list[ResearchQuestion]
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    respondents: list[Respondent] = Field(default_factory=list)
    # Free-form context that may help the LLM (product area, user tasks tested, etc.)
    context: Optional[str] = None

    def respondent_by_id(self, rid: str) -> Optional[Respondent]:
        for r in self.respondents:
            if r.id == rid:
                return r
        return None
