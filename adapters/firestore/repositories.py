"""Firestore-backed StatePort implementations (ADR-0004).

SDK stays in adapters/ only (F55). Collections:
  profiles/{user_id}
  portfolios/{id}
  portfolios/{id}/positions/{auto_id}
"""

from __future__ import annotations

from datetime import date
from typing import Any

from google.cloud.firestore import AsyncClient, FieldFilter

from core.config import LLMSettings
from core.portfolio.models import Portfolio, Position, Profile


def _client(project: str | None = None) -> AsyncClient:
    settings = LLMSettings()
    return AsyncClient(project=project or settings.gcp_project)


def _position_to_dict(position: Position) -> dict[str, Any]:
    data = position.model_dump()
    data["acquired"] = position.acquired.isoformat()
    return data


def _position_from_dict(data: dict[str, Any]) -> Position:
    raw = dict(data)
    acquired = raw.get("acquired")
    if isinstance(acquired, str):
        raw["acquired"] = date.fromisoformat(acquired)
    return Position.model_validate(raw)


class FirestoreProfileRepository:
    """profiles/{user_id}."""

    def __init__(self, client: AsyncClient | None = None, *, project: str | None = None) -> None:
        self._db = client or _client(project)

    async def get(self, user_id: str) -> Profile | None:
        snap = await self._db.collection("profiles").document(user_id).get()
        if not snap.exists:
            return None
        data = snap.to_dict() or {}
        data["user_id"] = user_id
        return Profile.model_validate(data)

    async def upsert(self, profile: Profile) -> None:
        payload = profile.model_dump()
        await self._db.collection("profiles").document(profile.user_id).set(payload)


class FirestorePortfolioRepository:
    """portfolios/{id} with user_id ownership on list."""

    def __init__(self, client: AsyncClient | None = None, *, project: str | None = None) -> None:
        self._db = client or _client(project)

    async def create(self, portfolio: Portfolio) -> str:
        payload = portfolio.model_dump()
        await self._db.collection("portfolios").document(portfolio.id).set(payload)
        return portfolio.id

    async def get(self, portfolio_id: str) -> Portfolio | None:
        snap = await self._db.collection("portfolios").document(portfolio_id).get()
        if not snap.exists:
            return None
        data = snap.to_dict() or {}
        data["id"] = portfolio_id
        return Portfolio.model_validate(data)

    async def list_for_user(self, user_id: str) -> list[Portfolio]:
        query = self._db.collection("portfolios").where(
            filter=FieldFilter("user_id", "==", user_id)
        )
        results: list[Portfolio] = []
        async for snap in query.stream():
            data = snap.to_dict() or {}
            data["id"] = snap.id
            portfolio = Portfolio.model_validate(data)
            # Defense in depth: never return another user's portfolio.
            if portfolio.user_id != user_id:
                continue
            results.append(portfolio)
        return results


class FirestorePositionRepository:
    """portfolios/{id}/positions/* — requires portfolio existence on add."""

    def __init__(self, client: AsyncClient | None = None, *, project: str | None = None) -> None:
        self._db = client or _client(project)

    async def _require_portfolio(self, portfolio_id: str) -> Portfolio:
        snap = await self._db.collection("portfolios").document(portfolio_id).get()
        if not snap.exists:
            raise ValueError(f"portfolio not found: {portfolio_id}")
        data = snap.to_dict() or {}
        data["id"] = portfolio_id
        return Portfolio.model_validate(data)

    async def add(self, portfolio_id: str, position: Position) -> None:
        # Ownership is carried on the parent portfolio; ensure it exists.
        await self._require_portfolio(portfolio_id)
        col = self._db.collection("portfolios").document(portfolio_id).collection("positions")
        await col.add(_position_to_dict(position))

    async def list(self, portfolio_id: str) -> list[Position]:
        # Read path: portfolio must exist (ownership checked by caller via portfolio.user_id).
        await self._require_portfolio(portfolio_id)
        col = self._db.collection("portfolios").document(portfolio_id).collection("positions")
        positions: list[Position] = []
        async for snap in col.stream():
            data = snap.to_dict() or {}
            positions.append(_position_from_dict(data))
        return positions
