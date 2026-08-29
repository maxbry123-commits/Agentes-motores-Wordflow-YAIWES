"""Stage 7.9 validation: check coded segments against constraints.

Two levels:
  1. During local coding: quote_matches_transcript is called per segment to trigger retries.
  2. After coding: validate_coded_transcript produces a report of soft warnings and hard errors.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Optional

from schemas import Brief, CodedSegment, CodedTranscript, RawTranscript


WHITESPACE_RE = re.compile(r"\s+")
PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_for_match(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace, NFC-normalize."""
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = PUNCT_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def quote_matches_transcript(
    quote: str,
    transcript_text: str,
    *,
    mode: str = "normalized",
    fuzzy_threshold: float = 0.92,
) -> bool:
    """Return True if the quote can be located in the transcript.

    Modes:
      - exact: strict substring
      - normalized: substring after normalization (recommended default)
      - fuzzy: SequenceMatcher ratio over a sliding window ≥ threshold
    """
    if not quote.strip():
        return False

    if mode == "exact":
        return quote in transcript_text

    norm_quote = normalize_for_match(quote)
    norm_transcript = normalize_for_match(transcript_text)

    if mode == "normalized":
        return norm_quote in norm_transcript

    if mode == "fuzzy":
        if norm_quote in norm_transcript:
            return True
        # Sliding window fuzzy match
        qlen = len(norm_quote)
        if qlen == 0 or qlen > len(norm_transcript):
            return False
        step = max(1, qlen // 4)
        for i in range(0, len(norm_transcript) - qlen + 1, step):
            window = norm_transcript[i:i + qlen + 10]
            if SequenceMatcher(None, norm_quote, window).ratio() >= fuzzy_threshold:
                return True
        return False

    raise ValueError(f"Unknown citation_match_mode: {mode}")


@dataclass
class SegmentIssue:
    segment_id: str
    severity: str  # "error" | "warning"
    code: str
    message: str


@dataclass
class ValidationReport:
    interview_id: str
    total_segments: int
    issues: list[SegmentIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[SegmentIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[SegmentIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def to_markdown(self) -> str:
        """Produce a short markdown report for humans."""
        lines = [
            f"# Validation report: {self.interview_id}",
            "",
            f"- Total segments: {self.total_segments}",
            f"- Errors: {len(self.errors)}",
            f"- Warnings: {len(self.warnings)}",
            "",
        ]
        if self.errors:
            lines.append("## Errors")
            lines.append("")
            for e in self.errors:
                lines.append(f"- **{e.segment_id}** [{e.code}]: {e.message}")
            lines.append("")
        if self.warnings:
            lines.append("## Warnings")
            lines.append("")
            for w in self.warnings:
                lines.append(f"- {w.segment_id} [{w.code}]: {w.message}")
            lines.append("")
        if not self.issues:
            lines.append("No issues found. ✅")
        return "\n".join(lines)


def validate_coded_transcript(
    coded: CodedTranscript,
    transcript: RawTranscript,
    brief: Brief,
    *,
    citation_match_mode: str = "normalized",
    fuzzy_threshold: float = 0.92,
) -> ValidationReport:
    """Check the coded transcript for consistency issues. Returns a report — does not raise."""
    report = ValidationReport(
        interview_id=coded.interview_id,
        total_segments=len(coded.segments),
    )

    valid_rq_ids = {rq.id for rq in brief.research_questions}
    valid_h_ids = {h.id for h in brief.hypotheses}
    transcript_text = transcript.full_text()

    for seg in coded.segments:
        # 1. Citation match
        if not quote_matches_transcript(
            seg.quote, transcript_text,
            mode=citation_match_mode, fuzzy_threshold=fuzzy_threshold,
        ):
            report.issues.append(SegmentIssue(
                segment_id=seg.segment_id,
                severity="error",
                code="citation_mismatch",
                message=f"Quote does not match transcript: {seg.quote[:80]!r}",
            ))

        # 2. Research question ids resolve
        for rq_id in seg.research_question_ids:
            if rq_id not in valid_rq_ids:
                report.issues.append(SegmentIssue(
                    segment_id=seg.segment_id,
                    severity="error",
                    code="unknown_research_question",
                    message=f"research_question_id {rq_id!r} not in brief",
                ))

        # 3. Hypothesis ids resolve
        for hs in seg.hypothesis_support:
            if hs.hypothesis_id not in valid_h_ids:
                report.issues.append(SegmentIssue(
                    segment_id=seg.segment_id,
                    severity="error",
                    code="unknown_hypothesis",
                    message=f"hypothesis_id {hs.hypothesis_id!r} not in brief",
                ))

        # 4. Subject codes sanity
        if not seg.subject_codes:
            report.issues.append(SegmentIssue(
                segment_id=seg.segment_id,
                severity="warning",
                code="empty_subject_codes",
                message="No subject_codes produced — segment may be tangential",
            ))
        for code in seg.subject_codes:
            if len(code) > 80:
                report.issues.append(SegmentIssue(
                    segment_id=seg.segment_id,
                    severity="warning",
                    code="code_too_long",
                    message=f"Subject code looks like a sentence, not a code: {code!r}",
                ))

        # 5. Internal warnings propagated from coding stage
        for w in seg.meta.validation_warnings:
            report.issues.append(SegmentIssue(
                segment_id=seg.segment_id,
                severity="warning",
                code="coding_warning",
                message=w,
            ))

    return report
