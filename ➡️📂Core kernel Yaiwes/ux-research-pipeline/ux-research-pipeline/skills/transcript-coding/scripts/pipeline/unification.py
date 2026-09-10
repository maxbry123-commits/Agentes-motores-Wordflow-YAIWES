"""Stage 7.9 — code unification.

Given a project codebook and a batch of new codes seen in freshly coded interviews,
proposes groupings: which new codes should merge with existing canonical entries or with
each other. Output is a proposal — no automatic renaming. The researcher reviews the
proposal (a CSV or JSON) and applies approved merges.
"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from backends import LLMBackend
from backends.base import LLMMessage
from schemas import CodedTranscript, ProjectCodebook, CodebookEntry

logger = logging.getLogger(__name__)


UNIFICATION_SCHEMA: dict[str, Any] = {
    "title": "UnificationProposal",
    "type": "object",
    "additionalProperties": False,
    "required": ["groups"],
    "properties": {
        "groups": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["canonical", "variants", "confidence", "rationale"],
                "properties": {
                    "canonical": {"type": "string"},
                    "variants": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "rationale": {"type": "string"},
                },
            },
        },
    },
}


def collect_new_codes(
    coded_interviews: list[CodedTranscript],
    codebook: ProjectCodebook,
) -> list[str]:
    """Return codes that appear in coded interviews but are not yet in the codebook."""
    existing = set()
    for entry in codebook.entries:
        existing.add(entry.canonical.strip().lower())
        for v in entry.variants:
            existing.add(v.strip().lower())

    seen = {}
    for ct in coded_interviews:
        for seg in ct.segments:
            for code in seg.subject_codes:
                key = code.strip().lower()
                if key in existing:
                    continue
                seen[key] = code.strip()  # keep original casing of first occurrence

    return sorted(seen.values(), key=str.lower)


def propose_unification(
    coded_interviews: list[CodedTranscript],
    codebook: ProjectCodebook,
    *,
    backend: LLMBackend,
    model: str,
    prompt_system: str,
    prompt_user: str,
    reasoning_effort: str = "low",
    max_tokens: int = 4000,
) -> dict[str, Any]:
    """Run the unification LLM call. Returns the raw proposal dict."""
    new_codes = collect_new_codes(coded_interviews, codebook)
    if not new_codes:
        logger.info("Unification: no new codes to process.")
        return {"groups": []}

    user = prompt_user.format(
        codebook_json=json.dumps(
            [e.model_dump() for e in codebook.entries], ensure_ascii=False, indent=2,
        ),
        new_codes_json=json.dumps(new_codes, ensure_ascii=False, indent=2),
    )
    messages = [
        LLMMessage(role="system", content=prompt_system),
        LLMMessage(role="user", content=user),
    ]
    logger.info("Unification: calling %s on %d new codes", model, len(new_codes))
    resp = backend.complete(
        messages=messages,
        model=model,
        response_schema=UNIFICATION_SCHEMA,
        reasoning_effort=reasoning_effort,
        max_tokens=max_tokens,
    )
    if resp.parsed is None:
        raise RuntimeError(f"Unification failed: unparseable JSON.\n{resp.text[:500]}")
    return resp.parsed


def write_unification_proposal_csv(proposal: dict[str, Any], path: Path) -> None:
    """Write the proposal as a CSV the researcher can review and edit.

    Columns: canonical, variant, confidence, approved (Y/N, empty for manual review), rationale
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["canonical", "variant", "confidence", "approved", "rationale"])
        for group in proposal.get("groups", []):
            canonical = group["canonical"]
            confidence = group.get("confidence", "")
            rationale = group.get("rationale", "")
            for variant in group.get("variants", []):
                writer.writerow([canonical, variant, confidence, "", rationale])


def apply_approved_merges(
    codebook: ProjectCodebook,
    approved_csv_path: Path,
    interview_id: str,
) -> ProjectCodebook:
    """Update the codebook by merging variants marked 'Y' in the approved column.

    Rows with approved='Y' are merged; others are skipped. Also handles adding brand-new
    canonical codes (when variant equals canonical and canonical is not in the book).
    """
    if not approved_csv_path.exists():
        logger.warning("No approved CSV at %s — nothing to apply.", approved_csv_path)
        return codebook

    by_canonical: dict[str, CodebookEntry] = {e.canonical: e for e in codebook.entries}

    with approved_csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            approved = row.get("approved", "").strip().upper()
            if approved not in {"Y", "YES", "TRUE", "1"}:
                continue
            canonical = row["canonical"].strip()
            variant = row["variant"].strip()
            if canonical not in by_canonical:
                by_canonical[canonical] = CodebookEntry(
                    canonical=canonical,
                    variants=[],
                    first_seen_interview=interview_id,
                    occurrences=0,
                )
            entry = by_canonical[canonical]
            if variant != canonical and variant not in entry.variants:
                entry.variants.append(variant)

    codebook.entries = list(by_canonical.values())
    return codebook


def save_codebook(codebook: ProjectCodebook, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(codebook.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8",
    )


def load_codebook(path: Path, project_id: str) -> ProjectCodebook:
    if not path.exists():
        return ProjectCodebook(project_id=project_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProjectCodebook(**data)
