"""Personal reference components for auditable AI-for-science agents."""

from .artifacts import AtomicArtifactWriter
from .contracts import (
    ExperimentResult,
    Proposal,
    RunSummary,
    StateView,
    TrialRecord,
    ValidationResult,
)
from .evidence import JsonlEvidenceLogger, redact
from .loop import ResearchLoop
from .validation import ScoreValidator

__all__ = [
    "AtomicArtifactWriter",
    "ExperimentResult",
    "JsonlEvidenceLogger",
    "Proposal",
    "ResearchLoop",
    "RunSummary",
    "ScoreValidator",
    "StateView",
    "TrialRecord",
    "ValidationResult",
    "redact",
]
