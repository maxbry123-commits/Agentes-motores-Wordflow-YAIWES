"""Gemini backend.

Uses google-genai client. Structured output via response_schema.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from .base import LLMBackend, LLMMessage, LLMResponse


class GeminiBackend(LLMBackend):
    name = "gemini"

    def __init__(self) -> None:
        try:
            from google import genai
        except ImportError as e:
            raise RuntimeError(
                "google-genai package is not installed. Run `pip install -r scripts/requirements.txt`."
            ) from e
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Add it to .env if you want to use the Gemini backend."
            )
        self._client = genai.Client(api_key=api_key)

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
        from google.genai import types as gtypes

        system_parts = [m.content for m in messages if m.role == "system"]
        system = "\n\n".join(system_parts) if system_parts else None
        # Gemini uses "contents" as the conversation; roles are "user" and "model".
        contents: list[Any] = []
        for m in messages:
            if m.role == "system":
                continue
            role = "user" if m.role == "user" else "model"
            parts: list[Any] = [gtypes.Part.from_text(text=m.content)]
            for img in m.images:
                if isinstance(img, bytes):
                    parts.append(gtypes.Part.from_bytes(data=img, mime_type="image/png"))
            contents.append(gtypes.Content(role=role, parts=parts))

        gen_config_kwargs: dict[str, Any] = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if system:
            gen_config_kwargs["system_instruction"] = system
        if response_schema is not None:
            gen_config_kwargs["response_mime_type"] = "application/json"
            gen_config_kwargs["response_schema"] = response_schema

        config = gtypes.GenerateContentConfig(**gen_config_kwargs)

        resp = self._client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        text = resp.text or ""
        parsed = None
        if response_schema is not None and text:
            import json
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None

        usage = getattr(resp, "usage_metadata", None)
        return LLMResponse(
            text=text,
            parsed=parsed,
            model=model,
            prompt_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
            completion_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
            raw=resp,
        )
