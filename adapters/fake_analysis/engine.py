"""In-memory AgentFrameworkPort for hermetic tests (no LLM / MCP)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from core.ports.agent_framework import (
    DEFAULT_DISCLAIMER,
    AnalysisRequest,
    AnalysisResult,
    Citation,
)


class FakeAnalysisEngine:
    """Returns a canned cited note without network."""

    def __init__(self, *, include_price: bool = True) -> None:
        self._include_price = include_price

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        price = Decimal("100.0") if self._include_price else None
        as_of = datetime(2024, 1, 1, tzinfo=UTC) if self._include_price else None
        currency = "USD" if self._include_price else None
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
            price_at_issue=price,
            price_as_of=as_of,
            currency=currency,
        )
