"""ADK implementation of AgentFrameworkPort (Vertex Gemini, keyless ADC)."""

from __future__ import annotations

import os
import uuid
from typing import Any

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

from core.analysis.stub_tools import get_quote as core_get_quote
from core.config import LLMSettings
from core.ports.agent_framework import AnalysisRequest, AnalysisResult

_AGENT_INSTRUCTION = (
    "You are a stock analyst. Use the get_quote tool to fetch the price, "
    "then give a one-sentence summary."
)


def get_quote(ticker: str) -> dict[str, Any]:
    """Get the latest stock quote for a ticker symbol.

    Thin adapter wrapper so ADK receives a JSON-serializable dict while core
    keeps the typed Quote model (F55: no ADK in core).
    """
    return core_get_quote(ticker).model_dump()


def _configure_vertex_env(settings: LLMSettings) -> None:
    """Point google-genai / ADK at Vertex AI using ADC (no API keys)."""
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.gcp_project
    os.environ["GOOGLE_CLOUD_LOCATION"] = settings.vertex_location


class AdkAnalysisEngine:
    """AgentFrameworkPort adapter backed by Google ADK + Vertex Gemini."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self._settings = settings or LLMSettings()
        _configure_vertex_env(self._settings)
        self._agent = Agent(
            name="stock_analyst",
            model=self._settings.gemini_model,
            instruction=_AGENT_INSTRUCTION,
            tools=[get_quote],
        )
        self._runner = InMemoryRunner(
            agent=self._agent,
            app_name="portfolio-copilot-spike",
        )

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run the ADK stock-analyst agent for ``request.ticker``."""
        session_id = f"spike-{uuid.uuid4()}"
        prompt = (
            f"Analyze ticker {request.ticker}. "
            "Call get_quote for this ticker, then summarize the price in one sentence."
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
            if event.content and event.content.parts:
                for part in event.content.parts:
                    text = part.text
                    if text:
                        summary_parts.append(text)

        summary = " ".join(summary_parts).strip()
        return AnalysisResult(
            ticker=request.ticker,
            summary=summary if summary else "(empty agent response)",
            tool_calls=tool_calls,
            framework="adk",
        )
