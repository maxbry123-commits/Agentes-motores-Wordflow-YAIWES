"""OpenAI backend for GPT-5.4 family.

Uses the Chat Completions API with structured outputs (response_format=json_schema).
Reasoning effort is passed as a top-level parameter for reasoning-capable models.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Optional

from .base import LLMBackend, LLMMessage, LLMResponse


class OpenAIBackend(LLMBackend):
    name = "openai"

    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "openai package is not installed. Run `pip install -r scripts/requirements.txt`."
            ) from e
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to .env in your working directory."
            )
        self._client = OpenAI(api_key=api_key)

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
        api_messages = [self._to_openai_message(m) for m in messages]

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": api_messages,
            "max_completion_tokens": max_tokens,
        }
        # GPT-5.x reasoning models ignore temperature — only send it for legacy chat models.
        if not model.startswith(("gpt-5", "o1", "o3", "o4")):
            kwargs["temperature"] = temperature

        # Reasoning effort parameter for GPT-5.4 family.
        if model.startswith(("gpt-5", "o1", "o3", "o4")) and reasoning_effort and reasoning_effort != "none":
            kwargs["reasoning_effort"] = reasoning_effort

        if response_schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.get("title", "response"),
                    "schema": response_schema,
                    "strict": True,
                },
            }

        resp = self._client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        text = choice.message.content or ""

        parsed: Optional[dict[str, Any]] = None
        if response_schema is not None and text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None

        usage = resp.usage
        return LLMResponse(
            text=text,
            parsed=parsed,
            model=resp.model,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            raw=resp,
        )

    @staticmethod
    def _to_openai_message(m: LLMMessage) -> dict[str, Any]:
        if not m.images:
            return {"role": m.role, "content": m.content}
        # Multimodal content: text + images.
        content: list[dict[str, Any]] = [{"type": "text", "text": m.content}]
        for img in m.images:
            if isinstance(img, bytes):
                b64 = base64.b64encode(img).decode("ascii")
                data_url = f"data:image/png;base64,{b64}"
            else:
                data_url = img  # assume already a URL or data URL
            content.append({
                "type": "image_url",
                "image_url": {"url": data_url},
            })
        return {"role": m.role, "content": content}
