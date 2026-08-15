"""In-memory TimeSeriesPort (hermetic tests + default backend)."""

from __future__ import annotations

from datetime import datetime

from core.tracking.models import Recommendation
from core.valuation.models import ValuationSnapshot


class InMemoryTimeSeriesStore:
    """Dict/list-backed TimeSeriesPort."""

    def __init__(self) -> None:
        self._snapshots: list[ValuationSnapshot] = []
        self._recommendations: list[Recommendation] = []

    async def write_valuation_snapshot(self, snapshot: ValuationSnapshot) -> None:
        self._snapshots.append(snapshot.model_copy(deep=True))

    async def query_valuation_history(
        self,
        portfolio_id: str,
        since: datetime,
        until: datetime,
    ) -> list[ValuationSnapshot]:
        rows = [
            s.model_copy(deep=True)
            for s in self._snapshots
            if s.portfolio_id == portfolio_id and since <= s.as_of <= until
        ]
        rows.sort(key=lambda s: s.as_of)
        return rows

    async def latest_valuation(self, portfolio_id: str) -> ValuationSnapshot | None:
        matching = [s for s in self._snapshots if s.portfolio_id == portfolio_id]
        if not matching:
            return None
        latest = max(matching, key=lambda s: s.as_of)
        return latest.model_copy(deep=True)

    async def write_recommendation(self, rec: Recommendation) -> None:
        self._recommendations.append(rec.model_copy(deep=True))

    async def query_recommendations(
        self,
        user_id: str | None = None,
        ticker: str | None = None,
        since: datetime | None = None,
    ) -> list[Recommendation]:
        rows: list[Recommendation] = []
        for rec in self._recommendations:
            if user_id is not None and rec.user_id != user_id:
                continue
            if ticker is not None and rec.ticker != ticker:
                continue
            if since is not None and rec.issued_at < since:
                continue
            rows.append(rec.model_copy(deep=True))
        rows.sort(key=lambda r: r.issued_at)
        return rows
