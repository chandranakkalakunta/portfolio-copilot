"""Hermetic TimeSeriesPort contract tests (in-memory fake — no GCP)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from adapters.memory.timeseries import InMemoryTimeSeriesStore
from core.ports.timeseries import TimeSeriesPort
from core.tracking.models import Recommendation
from core.valuation.models import ValuationSnapshot


def _ts(hour: int) -> datetime:
    return datetime(2026, 8, 15, hour, 0, 0, tzinfo=UTC)


def _snapshot(*, hour: int, value: str, portfolio_id: str = "pf-1") -> ValuationSnapshot:
    as_of = _ts(hour)
    return ValuationSnapshot(
        portfolio_id=portfolio_id,
        as_of=as_of,
        market_value=Decimal(value),
        cash=Decimal("100.00"),
        cost_basis=Decimal("50.00"),
        twr=Decimal("0.012"),
        mwr=None,
        currency="USD",
        source="test",
        created_at=as_of,
    )


def _rec(*, rec_id: str, user_id: str, ticker: str, hour: int) -> Recommendation:
    issued = _ts(hour)
    return Recommendation(
        rec_id=rec_id,
        user_id=user_id,
        portfolio_id="pf-1",
        ticker=ticker,
        market="US",
        action="hold",
        rating="informational",
        price_at_issue=Decimal("178.40"),
        price_as_of=issued,
        currency="USD",
        issued_at=issued,
        note_ref="note-1",
        model_attribution="adk",
    )


def test_timeseries_store_is_port() -> None:
    store: TimeSeriesPort = InMemoryTimeSeriesStore()
    assert callable(store.write_valuation_snapshot)
    assert callable(store.query_recommendations)


def test_valuation_round_trip_and_latest() -> None:
    async def _run() -> None:
        store = InMemoryTimeSeriesStore()
        first = _snapshot(hour=10, value="100.00")
        second = _snapshot(hour=12, value="110.50")
        other = _snapshot(hour=12, value="1.00", portfolio_id="pf-other")
        await store.write_valuation_snapshot(first)
        await store.write_valuation_snapshot(second)
        await store.write_valuation_snapshot(other)

        history = await store.query_valuation_history("pf-1", _ts(9), _ts(12))
        assert [s.market_value for s in history] == [Decimal("100.00"), Decimal("110.50")]
        assert all(isinstance(s.market_value, Decimal) for s in history)

        clipped = await store.query_valuation_history("pf-1", _ts(11), _ts(12))
        assert len(clipped) == 1
        assert clipped[0].market_value == Decimal("110.50")

        latest = await store.latest_valuation("pf-1")
        assert latest is not None
        assert latest.market_value == Decimal("110.50")
        assert await store.latest_valuation("missing") is None

    asyncio.run(_run())


def test_recommendation_round_trip_filters() -> None:
    async def _run() -> None:
        store = InMemoryTimeSeriesStore()
        await store.write_recommendation(_rec(rec_id="r1", user_id="alice", ticker="NVDA", hour=10))
        await store.write_recommendation(_rec(rec_id="r2", user_id="alice", ticker="AAPL", hour=11))
        await store.write_recommendation(_rec(rec_id="r3", user_id="bob", ticker="NVDA", hour=12))

        all_alice = await store.query_recommendations(user_id="alice")
        assert [r.rec_id for r in all_alice] == ["r1", "r2"]
        assert all(isinstance(r.price_at_issue, Decimal) for r in all_alice)

        nvda = await store.query_recommendations(ticker="NVDA")
        assert {r.rec_id for r in nvda} == {"r1", "r3"}

        recent = await store.query_recommendations(since=_ts(11))
        assert [r.rec_id for r in recent] == ["r2", "r3"]

        combo = await store.query_recommendations(user_id="alice", ticker="NVDA")
        assert [r.rec_id for r in combo] == ["r1"]

    asyncio.run(_run())


def test_query_window_is_inclusive() -> None:
    async def _run() -> None:
        store = InMemoryTimeSeriesStore()
        await store.write_valuation_snapshot(_snapshot(hour=10, value="1.00"))
        await store.write_valuation_snapshot(_snapshot(hour=11, value="2.00"))
        edge = await store.query_valuation_history("pf-1", _ts(10), _ts(10))
        assert len(edge) == 1
        assert edge[0].market_value == Decimal("1.00")

        since = _ts(10) + timedelta(seconds=1)
        assert await store.query_valuation_history("pf-1", since, _ts(10)) == []

    asyncio.run(_run())
