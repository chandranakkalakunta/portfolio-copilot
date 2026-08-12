"""Health / ready / version endpoint tests (O31)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "build_id" in body
    assert "deployed_at" in body


def test_ready() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_version() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert "build_id" in body
