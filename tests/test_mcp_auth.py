"""Hermetic MCP service-to-service auth tests (mocked token fetch; no network)."""

from __future__ import annotations

import pytest

from adapters.mcp_http import mcp_auth_required, mcp_origin, mcp_request_headers


def test_https_auto_attaches_bearer_header() -> None:
    headers = mcp_request_headers(
        "https://market-data.example.run.app/mcp",
        "auto",
        token_fetcher=lambda audience: f"tok-for-{audience}",
    )
    assert headers == {
        "Authorization": "Bearer tok-for-https://market-data.example.run.app",
    }


def test_http_auto_sends_no_token() -> None:
    def _fail(_audience: str) -> str:
        raise AssertionError("token fetch must not run for http://")

    headers = mcp_request_headers(
        "http://localhost:8081/mcp",
        "auto",
        token_fetcher=_fail,
    )
    assert headers == {}


def test_require_auth_true_overrides_http() -> None:
    headers = mcp_request_headers(
        "http://localhost:8081/mcp",
        "true",
        token_fetcher=lambda _audience: "forced",
    )
    assert headers["Authorization"] == "Bearer forced"


def test_require_auth_false_overrides_https() -> None:
    def _fail(_audience: str) -> str:
        raise AssertionError("token fetch must not run when require_auth=false")

    headers = mcp_request_headers(
        "https://market-data.example.run.app/mcp",
        "false",
        token_fetcher=_fail,
    )
    assert headers == {}


def test_mcp_origin_strips_path() -> None:
    assert mcp_origin("https://svc.run.app/mcp") == "https://svc.run.app"


@pytest.mark.parametrize(
    ("url", "flag", "expected"),
    [
        ("https://x.example/mcp", "auto", True),
        ("http://localhost:8081/mcp", "auto", False),
        ("http://localhost:8081/mcp", "true", True),
        ("https://x.example/mcp", "false", False),
    ],
)
def test_mcp_auth_required(url: str, flag: str, expected: bool) -> None:
    assert mcp_auth_required(url, flag) is expected
