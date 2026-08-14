"""MCP HTTP client helper — optional Cloud Run ID-token auth (adapters only).

Never imported by ``core/`` (F55). Local ``http://`` MCP stays token-free.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse

TokenFetcher = Callable[[str], str]


def mcp_origin(url: str) -> str:
    """Audience for a Cloud Run ID token: scheme + host, no path."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"invalid MCP URL: {url}")
    return f"{parsed.scheme}://{parsed.netloc}"


def mcp_auth_required(url: str, require_auth: str = "auto") -> bool:
    """Whether to attach a Google ID token.

    ``auto`` (default): https → yes, http → no.
    ``true`` / ``false`` override the scheme heuristic.
    """
    flag = require_auth.strip().lower()
    if flag in {"true", "1", "yes", "on"}:
        return True
    if flag in {"false", "0", "no", "off"}:
        return False
    return urlparse(url).scheme == "https"


def fetch_google_id_token(audience: str) -> str:
    """Mint an ID token via ADC (Cloud Run service-to-service)."""
    from google.auth.transport.requests import Request
    from google.oauth2 import id_token

    token = id_token.fetch_id_token(Request(), audience)  # type: ignore[no-untyped-call]
    if not isinstance(token, str) or not token:
        raise RuntimeError("failed to mint Google ID token for MCP")
    return token


def mcp_request_headers(
    url: str,
    require_auth: str = "auto",
    *,
    token_fetcher: TokenFetcher | None = None,
) -> dict[str, str]:
    """Authorization header for an MCP request, or empty when auth is off."""
    if not mcp_auth_required(url, require_auth):
        return {}
    fetcher = token_fetcher or fetch_google_id_token
    token = fetcher(mcp_origin(url))
    return {"Authorization": f"Bearer {token}"}


@asynccontextmanager
async def open_mcp_client(
    url: str,
    require_auth: str = "auto",
    *,
    token_fetcher: TokenFetcher | None = None,
) -> AsyncIterator[Any]:
    """Yield an ``mcp.Client``; attach a Bearer ID token when required."""
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client
    from mcp.shared._httpx_utils import create_mcp_http_client

    headers = mcp_request_headers(url, require_auth, token_fetcher=token_fetcher)
    if not headers:
        async with Client(url) as client:
            yield client
            return
    http = create_mcp_http_client(headers=headers)
    async with http, Client(streamable_http_client(url, http_client=http)) as client:
        yield client
