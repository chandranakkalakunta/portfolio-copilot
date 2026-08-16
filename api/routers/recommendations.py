"""Recommendation log read endpoint (auth-protected, user-scoped)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_timeseries_port
from core.ports.auth import AuthenticatedUser
from core.ports.timeseries import TimeSeriesPort
from core.tracking.models import Recommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
async def list_recommendations(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    store: Annotated[TimeSeriesPort, Depends(get_timeseries_port)],
    ticker: str | None = None,
    since: datetime | None = None,
) -> list[Recommendation]:
    """List recommendations issued for the current user only."""
    ticker_f = ticker.strip().upper() if ticker and ticker.strip() else None
    return await store.query_recommendations(
        user_id=user.user_id,
        ticker=ticker_f,
        since=since,
    )
