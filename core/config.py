"""Shared configuration (no cloud SDK imports — F55 / ADR-0001)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM / Vertex Gemini settings for adapters (not used by core at runtime yet).

    vertex_location defaults to us-central1 for Gemini availability even though the
    app region is asia-south1 (engineering-protocol §5.34). Model name is overridable
    and will be confirmed live in Phase 1.2.
    """

    model_config = SettingsConfigDict(env_prefix="PCOPILOT_")

    gcp_project: str = "pcopilot-dev"
    vertex_location: str = "us-central1"
    # Confirmed live in Phase 1.2 on Vertex (us-central1): gemini-2.5-flash
    gemini_model: str = "gemini-2.5-flash"


class MCPSettings(BaseSettings):
    """MCP client endpoints (HTTP microservices in all envs — ADR-0015)."""

    model_config = SettingsConfigDict(env_prefix="PCOPILOT_")

    # Streamable-HTTP MCP path on the market-data service.
    market_data_mcp_url: str = "http://localhost:8081/mcp"
    # ``auto`` = ID token when URL is https (private Cloud Run); never for http.
    # Override with ``true`` / ``false``.
    mcp_require_auth: str = "auto"


class FirebaseWebSettings(BaseSettings):
    """Public Firebase web client config (browser-safe apiKey). Never hardcode.

    Env: ``PCOPILOT_FIREBASE_API_KEY``, ``PCOPILOT_FIREBASE_AUTH_DOMAIN``,
    ``PCOPILOT_FIREBASE_PROJECT_ID``.
    """

    model_config = SettingsConfigDict(env_prefix="PCOPILOT_FIREBASE_")

    api_key: str = ""
    auth_domain: str = ""
    project_id: str = ""

    def is_complete(self) -> bool:
        return bool(self.api_key and self.auth_domain and self.project_id)
