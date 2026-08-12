"""Hermetic auth tests (FakeAuthAdapter — no network / no Firebase)."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from adapters.fake_auth.auth import FAKE_USER, FAKE_VALID_TOKEN, FakeAuthAdapter
from api.main import app
from core.ports.auth import AuthenticatedUser, AuthError


@pytest.fixture
def client() -> Iterator[TestClient]:
    """TestClient with FakeAuthAdapter forced on app.state."""
    with TestClient(app) as test_client:
        app.state.auth_port = FakeAuthAdapter()
        yield test_client


def test_fake_adapter_valid_token() -> None:
    async def _run() -> AuthenticatedUser:
        return await FakeAuthAdapter().verify_token(FAKE_VALID_TOKEN)

    user = asyncio.run(_run())
    assert user.user_id == FAKE_USER.user_id
    assert user.email == FAKE_USER.email


def test_fake_adapter_invalid_token() -> None:
    async def _run() -> None:
        await FakeAuthAdapter().verify_token("not-a-real-token")

    with pytest.raises(AuthError):
        asyncio.run(_run())


def test_me_returns_user(client: TestClient) -> None:
    response = client.get("/me", headers={"Authorization": f"Bearer {FAKE_VALID_TOKEN}"})
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "alice"
    assert body["email"] == "alice@example.com"


def test_me_missing_auth_401(client: TestClient) -> None:
    response = client.get("/me")
    assert response.status_code == 401


def test_me_invalid_token_401(client: TestClient) -> None:
    response = client.get("/me", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401


def test_me_malformed_header_401(client: TestClient) -> None:
    response = client.get("/me", headers={"Authorization": "Token not-bearer"})
    assert response.status_code == 401
