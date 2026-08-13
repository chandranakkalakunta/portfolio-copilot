"""HTTP request/response models for the portfolio API."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ProfileBody(BaseModel):
    """Profile fields owned by the authenticated user (user_id forced server-side)."""

    market: Literal["US", "IN"]
    risk_profile: str
    interests: list[str] = Field(default_factory=list)
    intent: str


class PortfolioCreate(BaseModel):
    """Create a portfolio for the current user."""

    id: str | None = None
    type: Literal["real", "paper"] = "paper"
    market: Literal["US", "IN"] = "US"
    cash: float = 0.0


class PositionCreate(BaseModel):
    """Add a position under a portfolio."""

    ticker: str
    quantity: float
    cost_basis: float
    acquired: date


class AnalyzeBody(BaseModel):
    """Single-ticker analyze request (portfolio-fit is Phase 4)."""

    ticker: str
