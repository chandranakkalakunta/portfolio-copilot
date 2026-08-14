"""Hermetic tests for the ADK adapter (no network / no GCP credentials)."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

from adapters.agent_adk.engine import AdkAnalysisEngine
from core.config import LLMSettings, MCPSettings
from core.ports.agent_framework import AgentFrameworkPort, AnalysisRequest, AnalysisResult


def test_adk_engine_is_agent_framework_port() -> None:
    """Structural: AdkAnalysisEngine satisfies AgentFrameworkPort (type-level)."""
    engine: AgentFrameworkPort = AdkAnalysisEngine(
        settings=LLMSettings(gemini_model="test-model"),
        mcp_settings=MCPSettings(market_data_mcp_url="http://localhost:9/mcp"),
        mcp_call=AsyncMock(return_value={}),
    )
    assert callable(engine.analyze)


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
        def __init__(self, parts: list[_FakePart], *, calls: list[Any] | None = None) -> None:
            self.content = _FakeContent(parts)
            self._calls = calls or []

        def get_function_calls(self) -> list[Any]:
            return list(self._calls)

        def get_function_responses(self) -> list[Any]:
            return []

    fake_events = [
        _FakeEvent([], calls=[_FakeFc()]),
        _FakeEvent(
            [
                _FakePart(
                    text="AAPL trades at 232.10 USD based on the market-data quote.",
                )
            ]
        ),
    ]

    async def _mcp(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "ticker": "AAPL",
            "price": 232.10,
            "currency": "USD",
            "as_of": "2024-01-01T00:00:00+00:00",
        }

    engine = AdkAnalysisEngine(
        settings=LLMSettings(gemini_model="test-model"),
        mcp_settings=MCPSettings(market_data_mcp_url="http://localhost:9/mcp"),
        mcp_call=_mcp,
    )
    engine._runner = AsyncMock()
    engine._runner.run_debug = AsyncMock(return_value=fake_events)
    result = asyncio.run(engine.analyze(AnalysisRequest(ticker="AAPL")))

    assert isinstance(result, AnalysisResult)
    assert result.framework == "adk"
    assert result.ticker == "AAPL"
    assert result.tool_calls == ["get_quote"]
    assert "232.10" in result.summary
