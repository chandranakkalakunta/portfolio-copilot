"""Tests for provider-agnostic ports."""

from core.ports.llm import LLMPort


class FakeLLM:
    """In-memory fake satisfying LLMPort."""

    def complete(self, prompt: str) -> str:
        return "canned-response"


def test_fake_llm_satisfies_protocol() -> None:
    fake: LLMPort = FakeLLM()
    assert isinstance(fake, FakeLLM)


def test_fake_llm_returns_canned_value() -> None:
    fake = FakeLLM()
    assert fake.complete("hello") == "canned-response"
