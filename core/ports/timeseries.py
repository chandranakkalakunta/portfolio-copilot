"""Time-series analytical port (ADR-0001, ADR-0004).

Implementations live in adapters/ (BigQuery, in-memory). Core never imports
cloud SDKs (F55). Money is Decimal on the domain models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from core.tracking.models import Recommendation
from core.valuation.models import ValuationSnapshot


class TimeSeriesPort(Protocol):
    """Append-only analytical store for valuations and recommendations."""

    async def write_valuation_snapshot(self, snapshot: ValuationSnapshot) -> None:
        """Persist one valuation snapshot."""
        ...

    async def query_valuation_history(
        self,
        portfolio_id: str,
        since: datetime,
        until: datetime,
    ) -> list[ValuationSnapshot]:
        """Return snapshots for ``portfolio_id`` with ``since`` ≤ as_of ≤ ``until``."""
        ...

    async def latest_valuation(self, portfolio_id: str) -> ValuationSnapshot | None:
        """Return the newest snapshot for ``portfolio_id``, or None."""
        ...

    async def write_recommendation(self, rec: Recommendation) -> None:
        """Persist one issued recommendation."""
        ...

    async def query_recommendations(
        self,
        user_id: str | None = None,
        ticker: str | None = None,
        since: datetime | None = None,
    ) -> list[Recommendation]:
        """Return recommendations matching the optional filters."""
        ...
