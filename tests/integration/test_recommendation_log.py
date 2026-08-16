"""Opt-in integration: recommendation log via BigQuery TimeSeriesPort.

Requires ``PCOPILOT_BQ_INTEGRATION=1`` and ADC (same as test_bigquery_store).
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from adapters.store_bigquery.store import BigQueryTimeSeriesStore
from core.ports.agent_framework import AnalysisResult
from core.ports.auth import AuthenticatedUser
from core.tracking.service import RecommendationLogService

pytestmark = pytest.mark.integration


def test_log_from_analysis_against_bq() -> None:
    if os.environ.get("PCOPILOT_BQ_INTEGRATION", "").lower() not in {"1", "true", "yes"}:
        pytest.skip("PCOPILOT_BQ_INTEGRATION not set")

    async def _run() -> None:
        store = BigQueryTimeSeriesStore()
        service = RecommendationLogService(store)
        now = datetime.now(UTC)
        result = AnalysisResult(
            ticker="NVDA",
            summary="integration",
            tool_calls=["get_quote"],
            framework="adk",
            price_at_issue=Decimal("178.40"),
            price_as_of=now,
            currency="USD",
        )
        rec = await service.log_from_analysis(result, AuthenticatedUser(user_id="itest-rec-log"))
        assert rec is not None
        found = await store.query_recommendations(user_id="itest-rec-log", ticker="NVDA")
        assert any(r.rec_id == rec.rec_id for r in found)

    asyncio.run(_run())
