"""Position endpoints (auth-protected; portfolio ownership enforced)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_current_user, get_portfolio_repo, get_position_repo
from api.routers.portfolios import _require_owned_portfolio
from api.schemas import PositionCreate
from core.portfolio.models import Position
from core.ports.auth import AuthenticatedUser
from core.ports.repositories import PortfolioRepository, PositionRepository

router = APIRouter(prefix="/portfolios/{portfolio_id}/positions", tags=["positions"])


@router.post("")
async def add_position(
    portfolio_id: str,
    body: PositionCreate,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    portfolios: Annotated[PortfolioRepository, Depends(get_portfolio_repo)],
    positions: Annotated[PositionRepository, Depends(get_position_repo)],
) -> Position:
    await _require_owned_portfolio(portfolio_id, user.user_id, portfolios)
    position = Position(**body.model_dump())
    await positions.add(portfolio_id, position)
    return position


@router.get("")
async def list_positions(
    portfolio_id: str,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    portfolios: Annotated[PortfolioRepository, Depends(get_portfolio_repo)],
    positions: Annotated[PositionRepository, Depends(get_position_repo)],
) -> list[Position]:
    await _require_owned_portfolio(portfolio_id, user.user_id, portfolios)
    return await positions.list(portfolio_id)
