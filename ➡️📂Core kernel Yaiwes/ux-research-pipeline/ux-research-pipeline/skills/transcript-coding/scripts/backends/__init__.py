from .base import LLMBackend, LLMMessage, LLMResponse
from .openai_backend import OpenAIBackend
from .anthropic_backend import AnthropicBackend
from .gemini_backend import GeminiBackend


def make_backend(name: str) -> LLMBackend:
    """Factory for backends by config name."""
    if name == "openai":
        return OpenAIBackend()
    if name == "anthropic":
        return AnthropicBackend()
    if name == "gemini":
        return GeminiBackend()
    raise ValueError(f"Unknown backend: {name}. Supported: openai, anthropic, gemini.")


__all__ = [
    "LLMBackend",
    "LLMMessage",
    "LLMResponse",
    "OpenAIBackend",
    "AnthropicBackend",
    "GeminiBackend",
    "make_backend",
]
