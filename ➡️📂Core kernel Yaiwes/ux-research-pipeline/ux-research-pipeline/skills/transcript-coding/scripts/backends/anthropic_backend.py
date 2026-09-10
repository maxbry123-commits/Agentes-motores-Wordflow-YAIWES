"""Anthropic backend for Claude models (default target: claude-opus-4-7).

Notes:
  - Structured output is done by asking the model to emit JSON inside a tool response or via
    prefilled assistant turn. We use prefill + strict JSON parsing for simplicity.
  - Reasoning effort parameter is ignored (Anthropic has extended thinking controls, not
    reasoning_effort). Future: map to a thinking budget if the user opts in.
"""
from __future__ import annotations

import base64
import json
import os
import re
from typing import Any, Optional

from .base import LLMBackend, LLMMessage, LLMResponse


class AnthropicBackend(LLMBackend):
    name = "anthropic"

    def __init__(self) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic package is not installed. Run `pip install -r scripts/requirements.txt`."
            ) from e
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Add it to .env if you want to use the Anthropic backend."
            )
        self._client = Anthropic(api_key=api_key)

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
        system_parts: list[str] = []
        api_messages: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
                continue
            api_messages.append(self._to_anthropic_message(m))

        # If a schema is requested, append the schema description to system and prefill the
        # assistant turn with "{" to force JSON. Parse from the combined text.
        system = "\n\n".join(system_parts)
        if response_schema is not None:
            schema_str = json.dumps(response_schema, ensure_ascii=False, indent=2)
            system += (
                "\n\nRespond with a single JSON object that strictly matches this schema. "
                "No prose, no markdown fences — only the JSON object.\n\n"
                f"Schema:\n{schema_str}"
            )
            api_messages.append({"role": "assistant", "content": "{"})

        resp = self._client.messages.create(
            model=model,
            system=system,
            messages=api_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        text_blocks = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        text = "".join(text_blocks)
        if response_schema is not None:
            # Re-attach the prefilled "{" if the model didn't echo it.
            text_for_parse = text if text.lstrip().startswith("{") else "{" + text

        parsed: Optional[dict[str, Any]] = None
        if response_schema is not None:
            parsed = self._parse_first_json_object(text_for_parse)

        usage = resp.usage
        return LLMResponse(
            text=text,
            parsed=parsed,
            model=resp.model,
            prompt_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
            raw=resp,
        )

    @staticmethod
    def _to_anthropic_message(m: LLMMessage) -> dict[str, Any]:
        if not m.images:
            return {"role": m.role, "content": m.content}
        content: list[dict[str, Any]] = []
        for img in m.images:
            if isinstance(img, bytes):
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(img).decode("ascii"),
                    },
                })
            elif isinstance(img, str) and img.startswith("data:"):
                # Already a data URL — strip the prefix and pass as base64
                header, _, b64 = img.partition(",")
                media_type = header.split(";")[0].removeprefix("data:") or "image/png"
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64},
                })
        content.append({"type": "text", "text": m.content})
        return {"role": m.role, "content": content}

    @staticmethod
    def _parse_first_json_object(text: str) -> Optional[dict[str, Any]]:
        """Find and parse the first {...} balanced object in text."""
        # Fast path
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Balanced braces scan
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        in_str = False
        escape = False
        for i, ch in enumerate(text[start:], start=start):
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        return None
        return None
