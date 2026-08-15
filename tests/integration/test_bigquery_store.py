"""Integration: BigQuery TimeSeriesPort against the dev dataset.

Opt-in: set ``PCOPILOT_BQ_INTEGRATION=1`` and have ADC for ``pcopilot-dev``.
Skipped in default CI (tables exist only after Coordinator terraform apply).
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from adapters.store_bigquery.store import BigQueryTimeSeriesStore
from core.tracking.models import Recommendation
from core.valuation.models import ValuationSnapshot

pytestmark = pytest.mark.integration


def _require_bq() -> None:
    if os.environ.get("PCOPILOT_BQ_INTEGRATION", "").lower() not in {"1", "true", "yes"}:
        pytest.skip("PCOPILOT_BQ_INTEGRATION not set")


def test_bq_valuation_and_recommendation_round_trip() -> None:
    _require_bq()

    async def _run() -> None:
        store = BigQueryTimeSeriesStore()
        now = datetime.now(UTC)
        portfolio_id = f"itest-pf-{uuid.uuid4().hex[:10]}"
        rec_id = f"itest-rec-{uuid.uuid4().hex[:10]}"
        user_id = f"itest-user-{uuid.uuid4().hex[:8]}"

        snap = ValuationSnapshot(
            portfolio_id=portfolio_id,
            as_of=now,
            market_value=Decimal("1234.56"),
            cash=Decimal("10.00"),
            cost_basis=Decimal("1000.00"),
            twr=Decimal("0.0500"),
            mwr=None,
            currency="USD",
            source="integration",
            created_at=now,
        )
        await store.write_valuation_snapshot(snap)
        latest = await store.latest_valuation(portfolio_id)
        assert latest is not None
        assert latest.portfolio_id == portfolio_id
        assert latest.market_value == Decimal("1234.56")

        rec = Recommendation(
            rec_id=rec_id,
            user_id=user_id,
            portfolio_id=portfolio_id,
            ticker="NVDA",
            market="US",
            action="hold",
            rating="informational",
            price_at_issue=Decimal("178.40"),
            price_as_of=now,
            currency="USD",
            issued_at=now,
            note_ref=None,
            model_attribution="test",
        )
        await store.write_recommendation(rec)
        found = await store.query_recommendations(user_id=user_id, ticker="NVDA")
        assert any(r.rec_id == rec_id for r in found)
        match = next(r for r in found if r.rec_id == rec_id)
        assert match.price_at_issue == Decimal("178.40")

    asyncio.run(_run())
