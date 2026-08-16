"""Recommendation logging (F29). Router delegates here — no BQ SDK."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from core.ports.agent_framework import AnalysisResult
from core.ports.auth import AuthenticatedUser
from core.ports.timeseries import TimeSeriesPort
from core.tracking.models import Recommendation

_log = logging.getLogger(__name__)


class RecommendationLogService:
    """Build and persist a Recommendation from an analysis result (non-fatal)."""

    def __init__(self, store: TimeSeriesPort) -> None:
        self._store = store
        self.writes_ok = 0
        self.skipped_no_price = 0
        self.write_failures = 0

    async def log_from_analysis(
        self,
        result: AnalysisResult,
        user: AuthenticatedUser,
    ) -> Recommendation | None:
        """Write a Recommendation. Skip if no price; never fail the caller."""
        if result.price_at_issue is None:
            self.skipped_no_price += 1
            _log.warning(
                "recommendation_skip_no_price ticker=%s user_id=%s",
                result.ticker,
                user.user_id,
            )
            return None
        rec_id = uuid.uuid4().hex
        issued_at = datetime.now(UTC)
        rec = Recommendation(
            rec_id=rec_id,
            user_id=user.user_id,
            portfolio_id=None,
            ticker=result.ticker,
            market="US",
            action="informational",
            rating=result.rating,
            price_at_issue=result.price_at_issue,
            price_as_of=result.price_as_of or issued_at,
            currency=result.currency or "USD",
            issued_at=issued_at,
            note_ref=rec_id,
            model_attribution=result.framework,
            schema_version=1,
        )
        try:
            await self._store.write_recommendation(rec)
        except Exception:  # noqa: BLE001 — write must never fail /analyze
            self.write_failures += 1
            _log.exception(
                "recommendation_write_failed rec_id=%s ticker=%s user_id=%s",
                rec_id,
                result.ticker,
                user.user_id,
            )
            return None
        self.writes_ok += 1
        return rec
