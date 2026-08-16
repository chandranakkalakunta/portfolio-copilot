"""Recommendation domain model (Decimal money — never float)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class Recommendation(BaseModel):
    """Issued recommendation with price-at-issue (analytical store, ADR-0004)."""

    rec_id: str
    user_id: str
    portfolio_id: str | None = None
    ticker: str
    market: str
    action: str
    rating: str
    price_at_issue: Decimal
    price_as_of: datetime
    currency: str
    issued_at: datetime
    note_ref: str | None = None
    model_attribution: str | None = None
    schema_version: int = Field(default=1)

    @field_serializer("price_at_issue", when_used="json")
    def _serialize_price_at_issue(self, value: Decimal) -> str:
        return format(value, "f")
