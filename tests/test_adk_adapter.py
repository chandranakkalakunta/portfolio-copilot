"""Hermetic tests for the ADK adapter (no network / no GCP credentials)."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from adapters.agent_adk.engine import AdkAnalysisEngine, get_quote
from core.config import LLMSettings
from core.ports.agent_framework import AgentFrameworkPort, AnalysisRequest, AnalysisResult


def test_adk_engine_is_agent_framework_port() -> None:
    """Structural: AdkAnalysisEngine satisfies AgentFrameworkPort (type-level)."""
    engine: AgentFrameworkPort = AdkAnalysisEngine(
        settings=LLMSettings(gemini_model="test-model"),
    )
    assert callable(engine.analyze)


def test_get_quote_tool_wrapper_returns_dict() -> None:
    payload = get_quote("aapl")
    assert payload["ticker"] == "AAPL"
    assert payload["price"] == 232.10
    assert payload["currency"] == "USD"


def test_analyze_with_monkeypatched_runner() -> None:
    """Network-free analyze path: fake run_debug events with tool call + text."""

    class _FakeFc:
        name = "get_quote"

    class _FakePart:
        def __init__(self, text: str | None = None, function_call: Any = None) -> None:
            self.text = text
            self.function_call = function_call

    class _FakeContent:
        def __init__(self, parts: list[_FakePart]) -> None:
            self.parts = parts

    class _FakeEvent:
        def __init__(self, parts: list[_FakePart]) -> None:
            self.content = _FakeContent(parts)

        def get_function_calls(self) -> list[_FakeFc]:
            return [_FakeFc() for p in self.content.parts if p.function_call]

    fake_events = [
        _FakeEvent([_FakePart(function_call=_FakeFc())]),
        _FakeEvent(
            [
                _FakePart(
                    text="AAPL trades at 232.10 USD based on the stub quote.",
                )
            ]
        ),
    ]

    engine = AdkAnalysisEngine(settings=LLMSettings(gemini_model="test-model"))
    with patch.object(
        engine._runner,
        "run_debug",
        new=AsyncMock(return_value=fake_events),
    ):
        result = asyncio.run(engine.analyze(AnalysisRequest(ticker="AAPL")))

    assert isinstance(result, AnalysisResult)
    assert result.framework == "adk"
    assert result.ticker == "AAPL"
    assert result.tool_calls == ["get_quote"]
    assert "232.10" in result.summary
