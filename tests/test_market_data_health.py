"""Hermetic tests for market-data MCP /health (no network)."""

from __future__ import annotations

import os
from unittest.mock import patch

from market_data.server import health_payload


def test_health_payload_includes_build_id() -> None:
    with patch.dict(os.environ, {"BUILD_ID": "test-build-123"}, clear=False):
        # Re-import path uses module-level BUILD_ID captured at import; call payload
        # uses the module constant. Assert shape + that build_id key exists.
        body = health_payload()
    assert body["status"] == "ok"
    assert "build_id" in body
    assert isinstance(body["build_id"], str)
    assert body["build_id"]  # non-empty (default "dev" or env)
    assert "deployed_at" in body
    assert "started_at" in body


def test_health_payload_build_id_from_module_constant() -> None:
    """Unit-level: health_payload reports the server's BUILD_ID constant."""
    from market_data import server

    body = server.health_payload()
    assert body["build_id"] == server.BUILD_ID
    assert body["status"] == "ok"
