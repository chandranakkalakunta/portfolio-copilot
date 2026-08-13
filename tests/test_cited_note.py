"""Hermetic tests for cited-note AnalysisResult via mocked MCP + LLM."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from adapters.agent_adk.engine import AdkAnalysisEngine
from core.config import LLMSettings, MCPSettings
from core.ports.agent_framework import DEFAULT_DISCLAIMER, AnalysisRequest, AnalysisResult


async def _fake_mcp(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    ticker = str(arguments.get("ticker", "AAPL")).upper()
    if name == "get_quote":
        return {
            "ticker": ticker,
            "price": 232.10,
            "currency": "USD",
            "as_of": "2024-06-01T12:00:00+00:00",
        }
    if name == "get_fundamentals":
        return {
            "ticker": ticker,
            "market_cap": 3.0e12,
            "trailing_pe": 28.5,
            "forward_pe": 26.0,
            "profit_margin": 0.25,
            "as_of": "2024-06-01T12:00:00+00:00",
        }
    raise ValueError(f"unexpected tool {name}")


def test_cited_note_has_citations_disclaimer_and_tool_calls() -> None:
    class _FakeFc:
        name = "get_quote"

    class _FakeFc2:
        name = "get_fundamentals"

    class _FakePart:
        def __init__(self, text: str | None = None, function_call: Any = None) -> None:
            self.text = text
            self.function_call = function_call
            self.function_response = None

    class _FakeContent:
        def __init__(self, parts: list[_FakePart]) -> None:
            self.parts = parts

    class _FakeEvent:
        def __init__(
            self,
            parts: list[_FakePart],
            *,
            calls: list[Any] | None = None,
            responses: list[Any] | None = None,
        ) -> None:
            self.content = _FakeContent(parts)
            self._calls = calls or []
            self._responses = responses or []

        def get_function_calls(self) -> list[Any]:
            return list(self._calls)

        def get_function_responses(self) -> list[Any]:
            return list(self._responses)

    class _FakeFr:
        def __init__(self, name: str, response: dict[str, Any]) -> None:
            self.name = name
            self.response = response

    fake_events = [
        _FakeEvent(
            [],
            calls=[_FakeFc(), _FakeFc2()],
            responses=[
                _FakeFr(
                    "get_quote",
                    {
                        "ticker": "AAPL",
                        "price": 232.10,
                        "currency": "USD",
                        "as_of": "2024-06-01T12:00:00+00:00",
                    },
                ),
                _FakeFr(
                    "get_fundamentals",
                    {
                        "ticker": "AAPL",
                        "market_cap": 3.0e12,
                        "trailing_pe": 28.5,
                        "as_of": "2024-06-01T12:00:00+00:00",
                    },
                ),
            ],
        ),
        _FakeEvent(
            [
                _FakePart(
                    text=(
                        "AAPL trades near 232.10 USD with a trailing P/E of 28.5 "
                        "(market-data MCP, as_of 2024-06-01)."
                    )
                )
            ]
        ),
    ]

    engine = AdkAnalysisEngine(
        settings=LLMSettings(gemini_model="test-model"),
        mcp_settings=MCPSettings(market_data_mcp_url="http://localhost:9/mcp"),
        mcp_call=_fake_mcp,
    )
    with patch.object(engine._runner, "run_debug", new=AsyncMock(return_value=fake_events)):
        result = asyncio.run(engine.analyze(AnalysisRequest(ticker="AAPL")))

    assert isinstance(result, AnalysisResult)
    assert result.framework == "adk"
    assert result.disclaimer == DEFAULT_DISCLAIMER
    assert result.disclaimer  # non-empty
    assert "get_quote" in result.tool_calls
    assert "get_fundamentals" in result.tool_calls
    assert result.citations, "expected non-empty citations"
    for citation in result.citations:
        assert citation.source == "market-data MCP"
        assert citation.as_of
        assert citation.detail
    assert result.rating == "informational"
