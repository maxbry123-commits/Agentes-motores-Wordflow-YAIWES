"""Abstract LLM backend interface.

The pipeline is written against this interface so any stage can be run on OpenAI,
Anthropic, or Gemini without code changes — the active backend is chosen per stage in config.yaml.

Design goals:
  - Unified message format (OpenAI-style role/content).
  - Optional structured output via JSON schema.
  - Optional image input for vision-enabled stages.
  - Reasoning effort parameter (currently only OpenAI uses it, others ignore).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LLMMessage:
    """Single message in a conversation.

    For vision input, include images in the `images` list (bytes or base64 strings).
    Each backend handles the conversion to its native format internally.
    """
    role: str  # "system" | "user" | "assistant"
    content: str
    images: list[bytes] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from the backend."""
    text: str
    # Parsed JSON if a schema was requested. None if no schema was used or parsing failed.
    parsed: Optional[dict[str, Any]] = None
    # Raw model identifier that served the response.
    model: str = ""
    # Token usage (best effort across backends).
    prompt_tokens: int = 0
    completion_tokens: int = 0
    # Backend-specific diagnostic payload.
    raw: Any = None


class LLMBackend(ABC):
    """Abstract backend. Implementations must not silently fall back between models."""

    name: str = "abstract"

    @abstractmethod
    def complete(
        self,
        messages: list[LLMMessage],
        model: str,
        *,
        response_schema: Optional[dict[str, Any]] = None,
        reasoning_effort: str = "medium",
        max_tokens: int = 4000,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Run a text (or text+vision) completion.

        Args:
            messages: ordered conversation.
            model: backend-specific model id.
            response_schema: JSON schema for structured output. If provided, the backend
                configures native structured output mode and parses the response.
            reasoning_effort: one of none/low/medium/high/xhigh. Only OpenAI reasoning
                models currently use this. Others ignore it.
            max_tokens: upper bound on completion tokens.
            temperature: sampling temperature. Default 0 for reproducibility during coding.
        """
        raise NotImplementedError

    def supports_vision(self) -> bool:
        """Whether this backend (with its currently configured model) supports image input.

        Default: True. Override in subclasses if needed.
        """
        return True
