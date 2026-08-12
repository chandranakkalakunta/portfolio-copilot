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
