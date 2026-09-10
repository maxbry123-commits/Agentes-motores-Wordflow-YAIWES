"""A concrete end-to-end workflow: customer-support ticket triage.

Three single-responsibility workers run in sequence, communicating only through
the shared state:

1. ``ClassifierWorker`` reads the raw ``ticket`` and writes a ``classification``
   (category, urgency, sentiment).
2. ``ExtractorWorker`` reads the ``ticket`` and writes ``extraction`` of the
   concrete facts (product, version, requested action).
3. ``ResponderWorker`` reads the ``ticket``, ``classification`` and
   ``extraction`` and writes a ``reply`` — a drafted customer response.

The responder step carries an evaluator and an ``improve_threshold``, so a weak
first draft triggers the Manager's self-improvement loop.

This module is backend-agnostic: it defines *what* the workflow is. The
``offline_demo`` and ``support_triage_workflow`` scripts decide *how* to run it
(mock backend vs. real Claude).
"""

from __future__ import annotations

from typing import Any, Dict

from agentic_workflow import (
    EvalResult,
    Pipeline,
    Step,
    Worker,
    WorkerResult,
    SharedState,
)

VALID_CATEGORIES = ["billing", "technical", "account", "feature_request", "other"]
VALID_URGENCIES = ["low", "medium", "high", "critical"]


class ClassifierWorker(Worker):
    """Assign a category, urgency, and sentiment to a support ticket."""

    name = "classifier"
    persona = "a precise customer-support triage analyst"
    input_keys = ("ticket",)
    output_key = "classification"
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": VALID_CATEGORIES},
            "urgency": {"type": "string", "enum": VALID_URGENCIES},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "neutral", "negative"],
            },
        },
        "required": ["category", "urgency", "sentiment"],
        "additionalProperties": False,
    }
    default_instruction = (
        "Classify the support ticket. Choose the single best category, the "
        "urgency implied by the customer's situation, and the overall sentiment "
        "of their message."
    )


class ExtractorWorker(Worker):
    """Pull the concrete, actionable facts out of the ticket."""

    name = "extractor"
    persona = "a careful information-extraction specialist"
    input_keys = ("ticket",)
    output_key = "extraction"
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "affected_version": {"type": "string"},
            "requested_action": {"type": "string"},
        },
        "required": ["product", "requested_action"],
        "additionalProperties": False,
    }
    default_instruction = (
        "Extract the product the customer mentions, the affected version if "
        "stated (use 'unknown' if not), and the concrete action they are asking "
        "for. Do not classify or editorialize."
    )


class ResponderWorker(Worker):
    """Draft a customer-facing reply from the upstream analysis."""

    name = "responder"
    persona = "an empathetic senior support engineer"
    input_keys = ("ticket", "classification", "extraction")
    output_key = "reply"
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "reply": {"type": "string"},
            "internal_note": {"type": "string"},
        },
        "required": ["reply"],
        "additionalProperties": False,
    }
    default_instruction = "Write a reply to the customer."


def responder_evaluator(result: WorkerResult, state: SharedState) -> EvalResult:
    """Score a drafted reply on a few cheap, objective heuristics.

    A real system would use an LLM-as-judge or human feedback; this evaluator is
    deliberately simple and deterministic so the self-improvement loop is easy to
    observe in the demos.
    """
    reply = str(result.output.get("reply", ""))
    classification = state.get("classification", {}) or {}
    category = str(classification.get("category", "")).replace("_", " ")

    score = 0.0
    feedback_parts = []

    # 1. Substance: a one-liner is not a real reply.
    if len(reply) >= 220:
        score += 0.4
    else:
        feedback_parts.append(
            "The reply is too short; acknowledge the issue, explain the next "
            "step, and set expectations."
        )

    # 2. Relevance: the reply should reflect the triaged category.
    if category and category.lower() in reply.lower():
        score += 0.3
    elif category:
        feedback_parts.append(
            f"Reference the issue type ('{category}') so the customer feels "
            f"understood."
        )

    # 3. Courtesy: open with a greeting / acknowledgement.
    if any(reply.lower().startswith(g) for g in ("hi", "hello", "thank", "thanks")):
        score += 0.3
    else:
        feedback_parts.append("Open with a warm greeting or acknowledgement.")

    return EvalResult(score=score, feedback=" ".join(feedback_parts))


def build_pipeline() -> Pipeline:
    """Assemble the three-stage triage pipeline."""
    return Pipeline(
        [
            Step(ClassifierWorker()),
            Step(ExtractorWorker()),
            Step(
                ResponderWorker(),
                evaluator=responder_evaluator,
                improve_threshold=0.9,
            ),
        ]
    )


SAMPLE_TICKET = (
    "Subject: Charged twice for my Pro plan this month\n\n"
    "Hi, I'm on the Acme Analytics Pro plan (version 3.2) and I just noticed two "
    "identical charges of $49 on my card for this billing cycle. I only have one "
    "subscription. Can you please refund the duplicate charge? This is the second "
    "month it has happened and it's getting frustrating."
)
