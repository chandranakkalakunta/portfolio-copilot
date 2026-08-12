"""State ports for profile / portfolio / positions (ADR-0001, ADR-0004).

Implementations live in adapters/ (Firestore, in-memory). Core never imports
cloud SDKs (F55). Per-user isolation is the caller's responsibility via
user_id / ownership checks on the ports' implementations.
"""

from __future__ import annotations

from typing import Protocol

from core.portfolio.models import Portfolio, Position, Profile


class ProfileRepository(Protocol):
    """Persistence for user profiles."""

    async def get(self, user_id: str) -> Profile | None:
        """Return the profile for ``user_id``, or None if missing."""
        ...

    async def upsert(self, profile: Profile) -> None:
        """Create or replace the profile document keyed by ``profile.user_id``."""
        ...


class PortfolioRepository(Protocol):
    """Persistence for portfolios."""

    async def create(self, portfolio: Portfolio) -> str:
        """Persist a portfolio; return its id."""
        ...

    async def get(self, portfolio_id: str) -> Portfolio | None:
        """Return a portfolio by id, or None if missing."""
        ...

    async def list_for_user(self, user_id: str) -> list[Portfolio]:
        """List portfolios owned by ``user_id`` only."""
        ...


class PositionRepository(Protocol):
    """Persistence for positions under a portfolio."""

    async def add(self, portfolio_id: str, position: Position) -> None:
        """Add a position under ``portfolio_id`` (ownership enforced by impl)."""
        ...

    async def list(self, portfolio_id: str) -> list[Position]:
        """List positions for ``portfolio_id``."""
        ...
