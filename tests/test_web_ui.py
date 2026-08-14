"""Hermetic UI wiring tests — /config from env + static index (no browser/network)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_config_returns_keys_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PCOPILOT_FIREBASE_API_KEY", "test-browser-key")
    monkeypatch.setenv("PCOPILOT_FIREBASE_AUTH_DOMAIN", "pcopilot-test.firebaseapp.com")
    monkeypatch.setenv("PCOPILOT_FIREBASE_PROJECT_ID", "pcopilot-test")
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == {
        "apiKey": "test-browser-key",
        "authDomain": "pcopilot-test.firebaseapp.com",
        "projectId": "pcopilot-test",
    }


def test_config_missing_env_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PCOPILOT_FIREBASE_API_KEY", raising=False)
    monkeypatch.delenv("PCOPILOT_FIREBASE_AUTH_DOMAIN", raising=False)
    monkeypatch.delenv("PCOPILOT_FIREBASE_PROJECT_ID", raising=False)
    response = client.get("/config")
    assert response.status_code == 503
    assert response.json()["detail"] == "firebase web config not set"


def test_index_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    body = response.text
    assert "Sign in with Google" in body
    assert "Not investment advice" in body


def test_app_js_served() -> None:
    response = client.get("/app.js")
    assert response.status_code == 200
    assert "signInWithPopup" in response.text
    assert "Authorization" in response.text
