"""LangGraph implementation of AgentFrameworkPort (Vertex Gemini, keyless ADC)."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent

from core.analysis.stub_tools import get_quote as core_get_quote
from core.config import LLMSettings
from core.ports.agent_framework import AnalysisRequest, AnalysisResult

# Same instruction text as adapters/agent_adk/engine.py (parity for Phase 1.4).
_AGENT_INSTRUCTION = (
    "You are a stock analyst. Use the get_quote tool to fetch the price, "
    "then give a one-sentence summary."
)


@tool("get_quote")
def get_quote(ticker: str) -> dict[str, Any]:
    """Get the latest stock quote for a ticker symbol.

    Thin adapter wrapper so LangGraph receives a JSON-serializable dict while
    core keeps the typed Quote model (F55: no LangChain in core).
    """
    return core_get_quote(ticker).model_dump()


def _message_text(content: Any) -> str:
    """Normalize AIMessage content (str | list of blocks) to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content)


def _tool_names_from_message(message: AIMessage) -> list[str]:
    names: list[str] = []
    for call in message.tool_calls or []:
        name: str | None
        if isinstance(call, dict):
            raw = call.get("name")
            name = raw if isinstance(raw, str) else None
        else:
            raw_name = getattr(call, "name", None)
            name = raw_name if isinstance(raw_name, str) else None
        if name and name not in names:
            names.append(name)
    return names


class LangGraphAnalysisEngine:
    """AgentFrameworkPort adapter backed by LangGraph + ChatVertexAI."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self._settings = settings or LLMSettings()
        self._llm = ChatVertexAI(
            model=self._settings.gemini_model,
            project=self._settings.gcp_project,
            location=self._settings.vertex_location,
        )
        # Idiomatic minimal ReAct agent (create_react_agent).
        self._graph = create_react_agent(
            model=self._llm,
            tools=[get_quote],
            prompt=_AGENT_INSTRUCTION,
            name="stock_analyst",
        )

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run the LangGraph stock-analyst agent for ``request.ticker``."""
        prompt = (
            f"Analyze ticker {request.ticker}. "
            "Call get_quote for this ticker, then summarize the price in one sentence."
        )
        result = await self._graph.ainvoke(
            {"messages": [HumanMessage(content=prompt)]},
        )
        messages: list[BaseMessage] = list(result.get("messages", []))

        tool_calls: list[str] = []
        summary = ""
        for message in messages:
            if isinstance(message, AIMessage):
                for name in _tool_names_from_message(message):
                    if name not in tool_calls:
                        tool_calls.append(name)
                text = _message_text(message.content).strip()
                if text:
                    summary = text

        return AnalysisResult(
            ticker=request.ticker,
            summary=summary if summary else "(empty agent response)",
            tool_calls=tool_calls,
            framework="langgraph",
        )
