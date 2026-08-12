"""LLM port — provider-agnostic interface (ADR-0001)."""

from typing import Protocol


class LLMPort(Protocol):
    """Provider-agnostic port for LLM completion (ADR-0001).

    Adapters implement this protocol; core must never import cloud SDKs.
    """

    def complete(self, prompt: str) -> str:
        """Return a completion for the given prompt."""
        ...
