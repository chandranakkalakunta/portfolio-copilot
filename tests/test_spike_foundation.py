"""Tests for Phase 1.1 spike foundation (port, stub tool, LLM config)."""

from __future__ import annotations

import asyncio

from core.analysis.stub_tools import Quote, get_quote
from core.config import LLMSettings
from core.ports.agent_framework import AgentFrameworkPort, AnalysisRequest, AnalysisResult


class FakeEngine:
    """In-memory fake satisfying AgentFrameworkPort."""

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        return AnalysisResult(
            ticker=request.ticker,
            summary="fake summary",
            tool_calls=["get_quote"],
            framework="fake",
        )


def test_get_quote_aapl() -> None:
    quote = get_quote("aapl")
    assert quote == Quote(ticker="AAPL", price=232.10, currency="USD")


def test_get_quote_default() -> None:
    quote = get_quote("xyz")
    assert quote == Quote(ticker="XYZ", price=100.0, currency="USD")


def test_analysis_result_validates() -> None:
    result = AnalysisResult(
        ticker="AAPL",
        summary="ok",
        tool_calls=["get_quote"],
        framework="fake",
    )
    assert result.ticker == "AAPL"
    assert result.framework == "fake"


def test_fake_engine_satisfies_protocol() -> None:
    engine: AgentFrameworkPort = FakeEngine()
    result = asyncio.run(engine.analyze(AnalysisRequest(ticker="AAPL")))
    assert result.summary == "fake summary"
    assert result.tool_calls == ["get_quote"]
    assert result.framework == "fake"


def test_llm_settings_defaults() -> None:
    settings = LLMSettings()
    assert settings.gcp_project == "pcopilot-dev"
    assert settings.vertex_location == "us-central1"
    assert settings.gemini_model == "gemini-2.5-flash"
