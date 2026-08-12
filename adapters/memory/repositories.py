"""In-memory StatePort implementations (hermetic tests + local dev)."""

from __future__ import annotations

from copy import deepcopy

from core.portfolio.models import Portfolio, Position, Profile


class InMemoryProfileRepository:
    """Dict-backed ProfileRepository."""

    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}

    async def get(self, user_id: str) -> Profile | None:
        profile = self._profiles.get(user_id)
        return profile.model_copy(deep=True) if profile is not None else None

    async def upsert(self, profile: Profile) -> None:
        self._profiles[profile.user_id] = profile.model_copy(deep=True)


class InMemoryPortfolioRepository:
    """Dict-backed PortfolioRepository with user isolation on list."""

    def __init__(self) -> None:
        self._portfolios: dict[str, Portfolio] = {}

    async def create(self, portfolio: Portfolio) -> str:
        self._portfolios[portfolio.id] = portfolio.model_copy(deep=True)
        return portfolio.id

    async def get(self, portfolio_id: str) -> Portfolio | None:
        portfolio = self._portfolios.get(portfolio_id)
        return portfolio.model_copy(deep=True) if portfolio is not None else None

    async def list_for_user(self, user_id: str) -> list[Portfolio]:
        return [p.model_copy(deep=True) for p in self._portfolios.values() if p.user_id == user_id]


class InMemoryPositionRepository:
    """Dict-backed PositionRepository keyed by portfolio_id."""

    def __init__(self, portfolios: InMemoryPortfolioRepository | None = None) -> None:
        self._positions: dict[str, list[Position]] = {}
        self._portfolios = portfolios

    async def add(self, portfolio_id: str, position: Position) -> None:
        if self._portfolios is not None:
            portfolio = await self._portfolios.get(portfolio_id)
            if portfolio is None:
                raise ValueError(f"portfolio not found: {portfolio_id}")
        self._positions.setdefault(portfolio_id, []).append(position.model_copy(deep=True))

    async def list(self, portfolio_id: str) -> list[Position]:
        if self._portfolios is not None:
            portfolio = await self._portfolios.get(portfolio_id)
            if portfolio is None:
                raise ValueError(f"portfolio not found: {portfolio_id}")
        return deepcopy(self._positions.get(portfolio_id, []))
