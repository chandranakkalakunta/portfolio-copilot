# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Phase 0.1: repo scaffolding, toolchain, CI skeleton
- Phase 0.2.2: keyless WIF pool/provider + deployer SA (Terraform), plan only
- Phase 0.2.3: GitHub Actions keyless GCP auth (WIF) identity check
- Phase 0.3.1: Artifact Registry + runtime SA + scoped deployer roles (Terraform, plan only)
- Phase 0.3.2: FastAPI hello service with /health /ready /version (build id + deploy time, O31); Dockerfile
- Phase 0.3.3: deploy-on-merge CD to Cloud Run (keyless WIF); Cloud Run service 'hello'
- Phase 1.1: AgentFrameworkPort + stub tool + LLM config (spike foundation)
- Phase 1.2: ADK adapter of the spike slice; first live Vertex Gemini call (gemini-2.5-flash)
- Phase 1.3: LangGraph adapter of the spike slice; live Vertex Gemini smoke
- Phase 2.1: market-data MCP server (yfinance) with get_quote/get_fundamentals
- Phase 2.2: portfolio/profile domain + Firestore repositories (StatePort)
- Phase 2.1.1: rename mcp/ → mcp_servers/ to avoid PyPI 'mcp' SDK shadowing
- Phase 2.3: backend auth — AuthPort + Firebase ID-token verification + /me (F58 backend half)
- Phase 2.2.1: market-data MCP over HTTP (ADR-0015) + Dockerfile + /health + compose
- Phase 2.3.1: codify APIs + Firestore in Terraform; environment-setup runbook
- Phase 2.3.2: CI hardening — pip-audit, gitleaks, coverage gate (65%)
- Phase 2.3.3: integration tests — Firestore emulator + MCP HTTP (O8/O11)
- Phase 2.4: fundamental agent → market-data MCP (HTTP) → cited note (F17/F25/F26/F27)
- Phase 2.5: auth-protected API (profile/portfolio/positions/analyze)
- Phase 2.6: minimal UI + real Google Sign-In; real-token e2e
- Phase 2.6 fix: verify Firebase ID tokens against the configured Firebase project id
- Phase 2.7.1: fix API Dockerfile to bundle core/adapters; CI image-build check
- Phase 2.7.2: runtime IAM — run-app (datastore/aiplatform/run.invoker) + mcp-run SA (plan only)
- Phase 2.7.3: lazy heavy imports (fast cold start) + MCP service-to-service ID-token auth
- Phase 2.7.4: deploy API (public) + market-data MCP (private) as two Cloud Run services on push to main; MCP-first URL wiring; cpu-boost + timeout 300 + min-instances 0; real firebase/firestore/adk config; grant gh-deployer roles/run.admin so api can be deployed public (setIamPolicy for allUsers)
- docs: Phase 2 doc-hygiene — reconcile backlog/STATUS with applied IAM + 2.7.4 deploy; Phase 2 complete
