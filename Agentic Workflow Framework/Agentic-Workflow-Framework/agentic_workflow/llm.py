"""Language-model backends.

The framework talks to an LLM through a small :class:`LLMBackend` protocol, so
the orchestration logic is fully decoupled from any particular provider or from
the network. Two implementations ship with the framework:

* :class:`AnthropicBackend` — the real backend. It calls Claude through the
  official ``anthropic`` SDK, using structured outputs to guarantee the worker's
  JSON contract. The API key is read from the ``ANTHROPIC_API_KEY`` environment
  variable by the SDK; it is never read from, or written to, source code.
* :class:`MockLLMBackend` — a deterministic, offline backend used by the tests
  and the offline demo. It lets the entire Manager/Worker/checkpoint/self-
  improvement machinery run with no API key and no network.

Both return the same :class:`LLMResponse`, so swapping one for the other is a
one-line change at the call site.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

try:  # Python 3.8+: typing.Protocol is available in the stdlib.
    from typing import Protocol, runtime_checkable
except ImportError:  # pragma: no cover - very old interpreters
    from typing_extensions import Protocol, runtime_checkable  # type: ignore

from .errors import BackendError

# Default model. Claude Opus 4.8 is Anthropic's most capable Opus-tier model;
# override per backend instance if you want a cheaper/faster tier.
DEFAULT_MODEL = "claude-opus-4-8"


@dataclass
class LLMResponse:
    """A normalized response from any backend.

    ``data`` is the parsed JSON object when a schema was requested (the common
    case for workers). ``text`` is always the raw assistant text.
    """

    text: str
    data: Optional[Dict[str, Any]]
    usage: Dict[str, Any] = field(default_factory=dict)
    model: str = ""


@runtime_checkable
class LLMBackend(Protocol):
    """The single method every backend must provide."""

    def generate(
        self,
        *,
        system: str,
        prompt: str,
        schema: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> LLMResponse:
        """Produce a completion.

        Args:
            system: The immutable persona + protocol system prompt.
            prompt: The rendered user prompt (task + inputs + output contract).
            schema: A JSON Schema the response must satisfy, or ``None``.
            context: Metadata about the call (``worker``, ``purpose``,
                ``instruction_version``). Real backends may log it; the mock
                backend uses it to pick a deterministic canned reply.
        """
        ...


class AnthropicBackend:
    """Backend backed by Claude via the official ``anthropic`` SDK."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        max_tokens: int = 4096,
        adaptive_thinking: bool = True,
        effort: Optional[str] = "high",
        client: Optional[Any] = None,
    ) -> None:
        """Create the backend.

        Args:
            model: Claude model id. Defaults to ``claude-opus-4-8``.
            max_tokens: Output cap. 4096 keeps non-streaming calls well under
                the SDK's HTTP timeout while leaving room for a drafted reply.
            adaptive_thinking: If ``True``, request adaptive thinking
                (``{"type": "adaptive"}``) — the recommended mode for current
                Claude models.
            effort: One of ``low|medium|high|max`` (or ``None`` to omit). Goes
                inside ``output_config``.
            client: Inject a pre-built ``anthropic.Anthropic`` client (handy for
                tests). If omitted, a default client is constructed, which reads
                ``ANTHROPIC_API_KEY`` from the environment.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.adaptive_thinking = adaptive_thinking
        self.effort = effort
        if client is not None:
            self._client = client
        else:
            try:
                import anthropic
            except ImportError as exc:  # pragma: no cover - depends on env
                raise BackendError(
                    "the 'anthropic' package is required for AnthropicBackend; "
                    "install it with `pip install anthropic`"
                ) from exc
            # Reads ANTHROPIC_API_KEY (or an `ant auth login` profile) from the
            # environment. Never hardcode a key.
            self._client = anthropic.Anthropic()

    def generate(
        self,
        *,
        system: str,
        prompt: str,
        schema: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> LLMResponse:
        output_config: Dict[str, Any] = {}
        if self.effort:
            output_config["effort"] = self.effort
        if schema:
            # Structured outputs: constrain the response to the worker's schema.
            output_config["format"] = {"type": "json_schema", "schema": schema}

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if output_config:
            kwargs["output_config"] = output_config
        if self.adaptive_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            message = self._client.messages.create(**kwargs)
        except Exception as exc:  # surface SDK/transport errors uniformly
            raise BackendError(f"Anthropic request failed: {exc}") from exc

        text = self._extract_text(message)
        data: Optional[Dict[str, Any]] = None
        if schema:
            data = self._parse_json(text, context)

        usage = self._extract_usage(message)
        model = getattr(message, "model", self.model)
        return LLMResponse(text=text, data=data, usage=usage, model=model)

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _extract_text(message: Any) -> str:
        parts = []
        for block in getattr(message, "content", []) or []:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", ""))
        return "".join(parts).strip()

    @staticmethod
    def _parse_json(text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not text:
            raise BackendError(
                f"empty response for worker '{context.get('worker', '?')}'"
            )
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise BackendError(
                f"response for worker '{context.get('worker', '?')}' was not "
                f"valid JSON: {exc}"
            ) from exc

    @staticmethod
    def _extract_usage(message: Any) -> Dict[str, Any]:
        usage = getattr(message, "usage", None)
        if usage is None:
            return {}
        return {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }


# Type of a mock handler: (call_index, context, prompt) -> dict
MockHandler = Callable[[int, Dict[str, Any], str], Dict[str, Any]]


class MockLLMBackend:
    """A deterministic, offline backend for tests and the offline demo.

    Register one handler per ``(purpose, worker)`` pair. Each handler receives
    the zero-based call index (so it can return a different result on a re-run,
    e.g. to simulate an improved draft), the call context, and the rendered
    prompt. Handlers return the JSON object the worker expects.
    """

    def __init__(self) -> None:
        self._handlers: Dict[Tuple[str, str], MockHandler] = {}
        self._counts: Dict[Tuple[str, str], int] = {}

    def register(
        self, worker: str, handler: MockHandler, *, purpose: str = "worker"
    ) -> "MockLLMBackend":
        self._handlers[(purpose, worker)] = handler
        return self

    def call_count(self, worker: str, *, purpose: str = "worker") -> int:
        return self._counts.get((purpose, worker), 0)

    def generate(
        self,
        *,
        system: str,
        prompt: str,
        schema: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> LLMResponse:
        key = (str(context.get("purpose", "worker")), str(context.get("worker", "")))
        handler = self._handlers.get(key)
        if handler is None:
            raise BackendError(f"no mock handler registered for {key}")
        index = self._counts.get(key, 0)
        self._counts[key] = index + 1
        data = handler(index, context, prompt)
        text = json.dumps(data, ensure_ascii=False)
        return LLMResponse(
            text=text,
            data=data if schema else None,
            usage={"input_tokens": 0, "output_tokens": 0},
            model="mock-backend",
        )
