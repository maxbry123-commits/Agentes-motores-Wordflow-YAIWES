"""Smoke tests for Pydantic schemas.

Run with: python3 -m pytest tests/test_schemas.py
Or standalone:     python3 tests/test_schemas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make scripts/ importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from schemas import (  # noqa: E402
    Brief,
    CodedTranscript,
    RawTranscript,
    TranscriptUtterance,
)


EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def test_load_example_transcript():
    data = json.loads((EXAMPLES_DIR / "input_transcript.json").read_text(encoding="utf-8"))
    utterances = [TranscriptUtterance(**u) for u in data]
    transcript = RawTranscript(interview_id="input_transcript", utterances=utterances)
    assert len(transcript.utterances) > 10
    assert all(u.start <= u.end for u in transcript.utterances)
    assert any("Interviewer" in u.speaker for u in transcript.utterances)
    assert any("Respondent" in u.speaker for u in transcript.utterances)


def test_load_example_brief():
    data = json.loads((EXAMPLES_DIR / "input_brief.json").read_text(encoding="utf-8"))
    brief = Brief(**data)
    assert brief.project_id == "TICKET-123"
    assert len(brief.research_questions) >= 3
    assert len(brief.hypotheses) >= 3
    assert brief.respondent_by_id("r_1") is not None
    assert brief.respondent_by_id("r_nonexistent") is None


def test_load_example_coded_output():
    data = json.loads((EXAMPLES_DIR / "output_coded.json").read_text(encoding="utf-8"))
    coded = CodedTranscript(**data)
    assert coded.project_id == "TICKET-123"
    assert len(coded.segments) >= 3
    # Every coded segment must have a quote and at least one subject code
    for seg in coded.segments:
        assert seg.quote, f"Empty quote in {seg.segment_id}"
        assert seg.subject_codes, f"Empty subject_codes in {seg.segment_id}"
        assert seg.respondent_id == "r_1"


def test_citation_normalization():
    from pipeline.validation import normalize_for_match, quote_matches_transcript

    transcript = "Yeah, there was some big survey, kind of a long one, I think."
    quote = "there was some big survey kind of a long one I think"

    assert normalize_for_match(transcript).startswith("yeah ")
    assert quote_matches_transcript(quote, transcript, mode="normalized")
    # Exact mode fails on the same input because punctuation differs
    assert not quote_matches_transcript(quote, transcript, mode="exact")


def run_all():
    import inspect
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failures += 1
    return failures


if __name__ == "__main__":
    sys.exit(0 if run_all() == 0 else 1)
