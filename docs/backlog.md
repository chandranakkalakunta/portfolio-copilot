# Project Backlog

Traceability of functional (F#), AI (A#), and operational (O#) requirements to implementation phases/PRs per Multi-Agent Engineering Protocol v4.0 (§7.7).

## Implemented / traceability

| ID | Item | Phase | Status | Evidence |
|----|------|-------|--------|----------|
| O1 | CI (lint, type-check, unit) | Phase 0.1 | ✓ Done | PR #1 |
| O2 | Keyless CD (WIF identity proven) | Phase 0.2.3 | ✓ Done | PR #4 |
| F55 | No cloud SDK in `core/` (guard test) | Phase 0.1 | ✓ Done | PR #1 |
| O31 | Verifiable deploys (build id + deploy time pattern on hello) | Phase 0.3.2–0.3.3 | ✓ Done | PR #8, #9 |
| O3 | Environments / rails | Phase 0 | Partial | In progress |
| O5 | Observability baseline | Phase 0 | Partial | In progress |
| O6 | IaC / deploy hardening | Phase 0–0.3 | Partial | In progress |
| ADR-0014 | FastAPI as web framework | Phase 0.3.2 | Accepted | Hello service on FastAPI |

## Functional

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| — | Web framework choice | Phase 6 | Deferred | UI stack; 2.6 is vanilla HTML/JS served by FastAPI. API uses FastAPI (ADR-0014) |
| F55 | No cloud SDK in core | Phase 0.1 | ✓ Done | Guard test + ADR-0001 |
| F5 / F6 | Manual holdings / profile store (StatePort) | Phase 2.2 | In progress | Domain + Firestore + in-memory repos; security rules / indexes later |
| F58 | Google Sign-In (backend + real-token e2e) | Phase 2.3–2.6 | ✓ Done | AuthPort + Firebase adapter + `/me` + vanilla UI `signInWithPopup`; Coordinator browser e2e |
| F45 | Minimal dashboard / UI skeleton | Phase 2.6 | Skeleton | `web/index.html` + `web/app.js` (sign-in, holding form, analyze); full dashboard = Phase 6 |
| F46 | Attribution + disclaimer on AI output | Phase 2.6 | Skeleton | Cited note renders summary, citations (`as_of`), disclaimer banner; full product surface = Phase 6 |
| F17 / F25 / F26 / F27 | Cited fundamental note (disclaimer + as-of sources) | Phase 2.4 | In progress | ADK → market-data MCP HTTP; full multi-agent verdict + portfolio-fit = Phase 4 |
| F1 / F5 / F6 / F17 | Auth-protected HTTP API (profile/portfolio/positions/analyze) | Phase 2.5 | In progress | FastAPI + FakeAuth/memory hermetic; live analyze via ADK+MCP |

## AI

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| ADR-0012 | Agent framework spike (ADK vs LangGraph) | Phase 1 | In progress | 1.1 foundation; 1.2 ADK (live); 1.3 LangGraph (live, parity); 1.4 compare |
| — | Confirmed Vertex Gemini model/region (Phase 1.2 live smoke) | Phase 1.2 | ✓ Done | `gemini-2.5-flash` @ `us-central1` (ADC/keyless); `gemini-2.0-flash` 404 in project |
| — | LangGraph adapter parity (same instruction/tool/model as ADK) | Phase 1.3 | ✓ Done | `create_react_agent` + `ChatVertexAI`; live smoke on AAPL |
| F57 | Market-data MCP (yfinance skeleton) | Phase 2.1 | ✓ Done | `get_quote` / `get_fundamentals`; swap to licensed/paid behind MarketDataPort later; India coverage partial |
| ADR-0015 | MCP HTTP microservices (all envs) | Phase 2.2.1–2.7.3 | ✓ Done (market-data) | streamable-HTTP + `/health`; private Cloud Run ID-token auth (https auto; http token-free) |

## Operational

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| O1 | CI skeleton | Phase 0.1 | ✓ Done | PR #1 |
| O2 | Keyless identity / CD auth | Phase 0.2.3 | ✓ Done | PR #4 |
| O3 | Multi-env | Phase 0 | Partial | In progress |
| O5 | Observability | Phase 0 | Partial | In progress |
| O6 | IaC baseline | Phase 0.3–2.3.1 | Partial → progress | WIF, AR, roles, CD; 2.3.1 APIs + Firestore in TF; rules/indexes + full multi-env later |
| O31 | Verifiable deploys | Phase 0.3.2–0.3.3 | ✓ Done | PR #8, #9 |
| O10 | Security / dep scanning + coverage | Phase 2.3.2 | In progress | pip-audit, gitleaks, coverage fail-under 65% (ratchet up over time); SHA-pin actions → Phase 9 |
| O8 / O11 | Integration tests (emulator + HTTP) | Phase 2.3.3 | In progress | Firestore emulator + MCP HTTP fake-provider suites; dedicated CI job |

## Infrastructure & Technical

| Item | Phase | Status | Notes |
|------|-------|--------|-------|
| Request billing quota increase before creating test/prod projects — billing account at 5-project limit. | Pre-0.2.x | Open | Blocks multi-env projects |
| Terraform state bucket created imperatively (bootstrap); consider `terraform import` later. | 0.2.x | Open | `gs://pcopilot-dev-tfstate` |
| Tighten WIF trust to specific branch/GitHub environment in 0.3 (currently repo-scoped). | 0.3 | Open | Currently `assertion.repository` only |
| Firestore security rules + composite indexes for portfolio queries | Phase 2.x | Open | After StatePort baseline (2.2) |
| Identity Platform Google-provider + OAuth client (console) | Phase 2.6 | Residual | UI + `/config` shipped; consent screen / Web client / authorized origin `http://localhost:8000` remain console-only |
| GET foreign portfolio returns 403 (leaks existence) → 404 | Phase 2.x | Open | Privacy: treat other-user resources as not found; 2.5 returns 403 `not portfolio owner` |
| API image packaging (core/adapters/api/web) + CI `docker-build` | Phase 2.7.1 | ✓ Done | Root Dockerfile bundles importable source; MCP stays its own image |
| Runtime IAM: run-app datastore/aiplatform/run.invoker + mcp-run SA | Phase 2.7.2 | Plan only | Apply after review; no SA keys |
| Tighten `roles/run.invoker` from project-scoped to service-level | Phase 2.7.x | Open | Project-scoped is acceptable for staging; prod should be MCP-service-only |
| Prod public ingress via LB + NEG | Phase 2.7.x | Open | Cloud Run stays private; public path is HTTPS LB → Serverless NEG |
| Domain Restricted Sharing exception for staging | Phase 2.7.3 | Open | Staging may need a DRS org-policy exception to allow limited public/test ingress; prod stays LB+NEG |
| Cloud Run cold-start: lazy ADK/LangGraph/Vertex imports | Phase 2.7.3 | ✓ Done | `import api.main` stays light; engine built on first `/analyze` |
| Private MCP service-to-service ID-token auth | Phase 2.7.3 | ✓ Done | `PCOPILOT_MCP_REQUIRE_AUTH` auto by URL scheme; adapters only (F55) |

## Deferred (seeded)

- **Web framework choice (UI)** — Phase 6
- **Real market-data MCP (licensed/paid provider)** — later; 2.1 yfinance is skeleton only (F57)
- **Agent framework decision** — Phase 1.2–1.4 (ADK vs LangGraph)
