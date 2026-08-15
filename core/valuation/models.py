"""Valuation snapshot domain model (Decimal money — never float)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ValuationSnapshot(BaseModel):
    """Point-in-time portfolio valuation (analytical store, ADR-0004)."""

    model_config = ConfigDict(arbitrary_types_allowed=False)

    portfolio_id: str
    as_of: datetime
    market_value: Decimal
    cash: Decimal | None = None
    cost_basis: Decimal | None = None
    twr: Decimal | None = None
    mwr: Decimal | None = None
    currency: str
    source: str
    created_at: datetime
    schema_version: int = Field(default=1)
