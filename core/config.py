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
