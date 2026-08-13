"""Portfolio endpoints (auth-protected, per-user isolation)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user, get_portfolio_repo
from api.schemas import PortfolioCreate
from core.portfolio.models import Portfolio
from core.ports.auth import AuthenticatedUser
from core.ports.repositories import PortfolioRepository

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


async def _require_owned_portfolio(
    portfolio_id: str,
    user_id: str,
    repo: PortfolioRepository,
) -> Portfolio:
    portfolio = await repo.get(portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="portfolio not found")
    if portfolio.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not portfolio owner")
    return portfolio


@router.post("")
async def create_portfolio(
    body: PortfolioCreate,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    repo: Annotated[PortfolioRepository, Depends(get_portfolio_repo)],
) -> Portfolio:
    portfolio_id = body.id or f"pf-{uuid.uuid4().hex[:12]}"
    portfolio = Portfolio(
        id=portfolio_id,
        user_id=user.user_id,
        type=body.type,
        market=body.market,
        cash=body.cash,
    )
    await repo.create(portfolio)
    return portfolio


@router.get("")
async def list_portfolios(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    repo: Annotated[PortfolioRepository, Depends(get_portfolio_repo)],
) -> list[Portfolio]:
    return await repo.list_for_user(user.user_id)


@router.get("/{portfolio_id}")
async def get_portfolio(
    portfolio_id: str,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    repo: Annotated[PortfolioRepository, Depends(get_portfolio_repo)],
) -> Portfolio:
    return await _require_owned_portfolio(portfolio_id, user.user_id, repo)
