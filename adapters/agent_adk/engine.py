"""ADK fundamental agent → market-data MCP (HTTP) → cited note.

Uses the installed ``mcp.Client`` streamable-HTTP client (ADR-0015). ADK's
``McpToolset`` cannot load against ``mcp`` 2.x (imports ``mcp.shared.session``,
removed in the SDK). Tools are ADK FunctionTools that call the MCP over HTTP.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from mcp import Client

from core.config import LLMSettings, MCPSettings
from core.ports.agent_framework import (
    DEFAULT_DISCLAIMER,
    AnalysisRequest,
    AnalysisResult,
    Citation,
)

_FUNDAMENTAL_INSTRUCTION = (
    "You are a fundamental equity analyst. For the given ticker, call get_quote "
    "and get_fundamentals, then write a short, factual assessment. Every figure "
    "must be attributed to its source and as_of. Give no guarantees or promises "
    "of return. This is informational only, not investment advice."
)

McpCallFn = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]


def _tool_result_to_dict(result: Any) -> dict[str, Any]:
    """Normalize MCP CallToolResult / raw dict into a plain mapping."""
    if isinstance(result, dict):
        return result
    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured
    content = getattr(result, "content", None) or []
    texts: list[str] = []
    for block in content:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            texts.append(text)
    if len(texts) == 1:
        try:
            parsed = json.loads(texts[0])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"raw": texts[0]}
    if texts:
        return {"raw": texts}
    return {"raw": str(result)}


def _citations_from_tool_payloads(
    payloads: dict[str, dict[str, Any]],
) -> list[Citation]:
    """Build citations from get_quote / get_fundamentals MCP payloads."""
    citations: list[Citation] = []
    quote = payloads.get("get_quote")
    if quote:
        as_of = str(quote.get("as_of") or "unknown")
        citations.append(
            Citation(
                source="market-data MCP",
                as_of=as_of,
                detail=(
                    f"price={quote.get('price')} {quote.get('currency')} "
                    f"ticker={quote.get('ticker')}"
                ),
            )
        )
    fundamentals = payloads.get("get_fundamentals")
    if fundamentals:
        as_of = str(fundamentals.get("as_of") or "unknown")
        citations.append(
            Citation(
                source="market-data MCP",
                as_of=as_of,
                detail=(
                    f"market_cap={fundamentals.get('market_cap')} "
                    f"trailing_pe={fundamentals.get('trailing_pe')} "
                    f"forward_pe={fundamentals.get('forward_pe')} "
                    f"profit_margin={fundamentals.get('profit_margin')} "
                    f"ticker={fundamentals.get('ticker')}"
                ),
            )
        )
    return citations


def _configure_vertex_env(settings: LLMSettings) -> None:
    """Point google-genai / ADK at Vertex AI using ADC (no API keys)."""
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.gcp_project
    os.environ["GOOGLE_CLOUD_LOCATION"] = settings.vertex_location


class AdkAnalysisEngine:
    """AgentFrameworkPort: ADK + Vertex Gemini + market-data MCP over HTTP."""

    def __init__(
        self,
        settings: LLMSettings | None = None,
        mcp_settings: MCPSettings | None = None,
        *,
        mcp_call: McpCallFn | None = None,
    ) -> None:
        self._settings = settings or LLMSettings()
        self._mcp_settings = mcp_settings or MCPSettings()
        self._mcp_url = self._mcp_settings.market_data_mcp_url
        self._mcp_call = mcp_call
        # Captured tool payloads for citation building (filled during tool calls).
        self._last_tool_payloads: dict[str, dict[str, Any]] = {}

        _configure_vertex_env(self._settings)

        engine = self

        async def get_quote(ticker: str) -> dict[str, Any]:
            """Get the latest stock quote for a ticker symbol via market-data MCP."""
            return await engine._invoke_mcp("get_quote", {"ticker": ticker})

        async def get_fundamentals(ticker: str) -> dict[str, Any]:
            """Get curated fundamentals for a ticker via market-data MCP."""
            return await engine._invoke_mcp("get_fundamentals", {"ticker": ticker})

        self._agent = Agent(
            name="fundamental_analyst",
            model=self._settings.gemini_model,
            instruction=_FUNDAMENTAL_INSTRUCTION,
            tools=[get_quote, get_fundamentals],
        )
        self._runner = InMemoryRunner(
            agent=self._agent,
            app_name="portfolio-copilot-fundamental",
        )

    async def _invoke_mcp(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._mcp_call is not None:
            payload = await self._mcp_call(name, arguments)
        else:
            async with Client(self._mcp_url) as client:
                result = await client.call_tool(name, arguments)
                payload = _tool_result_to_dict(result)
        self._last_tool_payloads[name] = payload
        return payload

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run the fundamental analyst for ``request.ticker`` via MCP tools."""
        self._last_tool_payloads = {}
        session_id = f"fundamental-{uuid.uuid4()}"
        prompt = (
            f"Analyze ticker {request.ticker}. "
            "Call get_quote and get_fundamentals for this ticker, then write a "
            "short factual assessment with every figure attributed to market-data "
            "MCP and its as_of timestamp."
        )
        events = await self._runner.run_debug(
            prompt,
            user_id="spike-user",
            session_id=session_id,
            quiet=True,
            verbose=False,
        )

        tool_calls: list[str] = []
        summary_parts: list[str] = []
        for event in events:
            for fc in event.get_function_calls():
                name = fc.name
                if name and name not in tool_calls:
                    tool_calls.append(name)
            # Also record names from function responses (tool completed).
            for fr in event.get_function_responses():
                name = getattr(fr, "name", None)
                if name and name not in tool_calls:
                    tool_calls.append(name)
                response = getattr(fr, "response", None)
                if name and isinstance(response, dict):
                    self._last_tool_payloads.setdefault(name, response)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    text = part.text
                    if text:
                        summary_parts.append(text)

        summary = " ".join(summary_parts).strip()
        citations = _citations_from_tool_payloads(self._last_tool_payloads)
        return AnalysisResult(
            ticker=request.ticker,
            summary=summary if summary else "(empty agent response)",
            tool_calls=tool_calls,
            framework="adk",
            citations=citations,
            disclaimer=DEFAULT_DISCLAIMER,
            rating="informational",
        )
