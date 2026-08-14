"""Hermetic Firebase adapter tests — project-id resolution only (no network / no token)."""

from __future__ import annotations

import pytest

from adapters.firebase_auth.auth import FirebaseAuthAdapter, _resolve_firebase_project_id


def test_resolve_prefers_firebase_project_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PCOPILOT_FIREBASE_PROJECT_ID", "pcopilot-dev-d0a08")
    monkeypatch.setenv("PCOPILOT_GCP_PROJECT", "pcopilot-dev")
    assert _resolve_firebase_project_id() == "pcopilot-dev-d0a08"


def test_resolve_falls_back_to_gcp_project(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PCOPILOT_FIREBASE_PROJECT_ID", raising=False)
    monkeypatch.setenv("PCOPILOT_GCP_PROJECT", "pcopilot-dev")
    assert _resolve_firebase_project_id() == "pcopilot-dev"


def test_resolve_explicit_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PCOPILOT_FIREBASE_PROJECT_ID", "pcopilot-dev-d0a08")
    assert _resolve_firebase_project_id("explicit-project") == "explicit-project"


def test_adapter_uses_resolved_firebase_project_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PCOPILOT_FIREBASE_PROJECT_ID", "pcopilot-dev-d0a08")
    monkeypatch.setenv("PCOPILOT_GCP_PROJECT", "pcopilot-dev")
    monkeypatch.setattr(
        "adapters.firebase_auth.auth._ensure_firebase_app",
        lambda _project_id: None,
    )
    adapter = FirebaseAuthAdapter()
    assert adapter._project_id == "pcopilot-dev-d0a08"
