"""Hermetic tests for the LangGraph adapter (no network / no GCP credentials)."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from adapters.agent_langgraph.engine import LangGraphAnalysisEngine, get_quote
from core.config import LLMSettings
from core.ports.agent_framework import AgentFrameworkPort, AnalysisRequest, AnalysisResult


def test_langgraph_engine_is_agent_framework_port() -> None:
    """Structural: class has analyze; construction patched to avoid Vertex client."""
    with (
        patch("adapters.agent_langgraph.engine.ChatVertexAI") as mock_llm_cls,
        patch("adapters.agent_langgraph.engine.create_react_agent") as mock_create,
    ):
        mock_llm_cls.return_value = MagicMock(name="llm")
        mock_create.return_value = MagicMock(name="graph")
        engine: AgentFrameworkPort = LangGraphAnalysisEngine(
            settings=LLMSettings(gemini_model="test-model"),
        )
        assert callable(engine.analyze)


def test_get_quote_tool_wrapper_returns_dict() -> None:
    payload = get_quote.invoke({"ticker": "aapl"})
    assert payload["ticker"] == "AAPL"
    assert payload["price"] == 232.10
    assert payload["currency"] == "USD"
    assert get_quote.name == "get_quote"


def test_analyze_with_monkeypatched_graph() -> None:
    """Network-free analyze path: fake ainvoke messages with tool call + text."""
    fake_messages: list[Any] = [
        HumanMessage(content="Analyze ticker AAPL."),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "get_quote",
                    "args": {"ticker": "AAPL"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(
            content='{"ticker":"AAPL","price":232.1,"currency":"USD"}', tool_call_id="call-1"
        ),
        AIMessage(content="AAPL trades at 232.10 USD based on the stub quote."),
    ]

    with (
        patch("adapters.agent_langgraph.engine.ChatVertexAI") as mock_llm_cls,
        patch("adapters.agent_langgraph.engine.create_react_agent") as mock_create,
    ):
        mock_llm_cls.return_value = MagicMock(name="llm")
        graph = MagicMock(name="graph")
        graph.ainvoke = AsyncMock(return_value={"messages": fake_messages})
        mock_create.return_value = graph

        engine = LangGraphAnalysisEngine(settings=LLMSettings(gemini_model="test-model"))
        result = asyncio.run(engine.analyze(AnalysisRequest(ticker="AAPL")))

    assert isinstance(result, AnalysisResult)
    assert result.framework == "langgraph"
    assert result.ticker == "AAPL"
    assert result.tool_calls == ["get_quote"]
    assert "232.10" in result.summary
