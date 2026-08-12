"""Portfolio / profile domain models (no cloud SDKs — F55 / ADR-0001)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """User investing profile (preferences, market, risk)."""

    user_id: str
    market: Literal["US", "IN"]
    risk_profile: str
    interests: list[str] = Field(default_factory=list)
    intent: str


class Portfolio(BaseModel):
    """A real or paper portfolio owned by a user."""

    id: str
    user_id: str
    type: Literal["real", "paper"]
    market: Literal["US", "IN"]
    cash: float


class Position(BaseModel):
    """A holding within a portfolio."""

    ticker: str
    quantity: float
    cost_basis: float
    acquired: date
