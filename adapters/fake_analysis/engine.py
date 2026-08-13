"""In-memory AgentFrameworkPort for hermetic tests (no LLM / MCP)."""

from __future__ import annotations

from core.ports.agent_framework import (
    DEFAULT_DISCLAIMER,
    AnalysisRequest,
    AnalysisResult,
    Citation,
)


class FakeAnalysisEngine:
    """Returns a canned cited note without network."""

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        return AnalysisResult(
            ticker=request.ticker,
            summary=f"Fake fundamental note for {request.ticker.upper()}.",
            tool_calls=["get_quote", "get_fundamentals"],
            framework="fake",
            citations=[
                Citation(
                    source="fake",
                    as_of="2024-01-01T00:00:00+00:00",
                    detail=f"price=100.0 USD ticker={request.ticker.upper()}",
                )
            ],
            disclaimer=DEFAULT_DISCLAIMER,
            rating="informational",
        )
