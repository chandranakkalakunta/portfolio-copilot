"""Hermetic API tests — FakeAuth + in-memory repos + FakeAnalysisEngine."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from adapters.fake_analysis.engine import FakeAnalysisEngine
from adapters.fake_auth.auth import (
    FAKE_TOKEN_BOB,
    FAKE_USER,
    FAKE_USER_BOB,
    FAKE_VALID_TOKEN,
    FakeAuthAdapter,
)
from adapters.memory.repositories import (
    InMemoryPortfolioRepository,
    InMemoryPositionRepository,
    InMemoryProfileRepository,
)
from api.main import app
from core.ports.agent_framework import DEFAULT_DISCLAIMER


@pytest.fixture
def client() -> Iterator[TestClient]:
    profiles = InMemoryProfileRepository()
    portfolios = InMemoryPortfolioRepository()
    positions = InMemoryPositionRepository(portfolios)
    with TestClient(app) as test_client:
        app.state.auth_port = FakeAuthAdapter(
            token_map={
                FAKE_VALID_TOKEN: FAKE_USER,
                FAKE_TOKEN_BOB: FAKE_USER_BOB,
            }
        )
        app.state.profile_repo = profiles
        app.state.portfolio_repo = portfolios
        app.state.position_repo = positions
        app.state.analysis_engine = FakeAnalysisEngine()
        yield test_client


def _auth(token: str = FAKE_VALID_TOKEN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_portfolio_401_without_token(client: TestClient) -> None:
    assert client.get("/portfolios").status_code == 401


def test_create_get_portfolio_and_positions(client: TestClient) -> None:
    create = client.post(
        "/portfolios",
        headers=_auth(),
        json={"id": "pf-alice-1", "type": "paper", "market": "US", "cash": 5000},
    )
    assert create.status_code == 200
    body = create.json()
    assert body["id"] == "pf-alice-1"
    assert body["user_id"] == "alice"

    got = client.get("/portfolios/pf-alice-1", headers=_auth())
    assert got.status_code == 200
    assert got.json()["cash"] == 5000

    add = client.post(
        "/portfolios/pf-alice-1/positions",
        headers=_auth(),
        json={
            "ticker": "AAPL",
            "quantity": 10,
            "cost_basis": 150.0,
            "acquired": "2024-01-15",
        },
    )
    assert add.status_code == 200
    assert add.json()["ticker"] == "AAPL"

    listed = client.get("/portfolios/pf-alice-1/positions", headers=_auth())
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_analyze_returns_cited_note(client: TestClient) -> None:
    response = client.post("/analyze", headers=_auth(), json={"ticker": "AAPL"})
    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["disclaimer"] == DEFAULT_DISCLAIMER
    assert body["disclaimer"]
    assert body["citations"]
    assert "get_quote" in body["tool_calls"]
    assert body["price_at_issue"] == "100.0"


def test_user_b_cannot_read_user_a_portfolio(client: TestClient) -> None:
    create = client.post(
        "/portfolios",
        headers=_auth(FAKE_VALID_TOKEN),
        json={"id": "pf-secret", "type": "paper", "market": "US", "cash": 1},
    )
    assert create.status_code == 200

    # Bob lists only own portfolios
    bob_list = client.get("/portfolios", headers=_auth(FAKE_TOKEN_BOB))
    assert bob_list.status_code == 200
    assert bob_list.json() == []

    # Bob cannot GET Alice's portfolio
    bob_get = client.get("/portfolios/pf-secret", headers=_auth(FAKE_TOKEN_BOB))
    assert bob_get.status_code == 403
