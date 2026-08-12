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
| — | Web framework choice | Phase 6 | Deferred | UI stack; API uses FastAPI (ADR-0014) |
| F55 | No cloud SDK in core | Phase 0.1 | ✓ Done | Guard test + ADR-0001 |
| F5 / F6 | Manual holdings / profile store (StatePort) | Phase 2.2 | In progress | Domain + Firestore + in-memory repos; security rules / indexes later |
| F58 | Google Sign-In (backend ID-token verification) | Phase 2.3 | ✓ Backend done | AuthPort + Firebase adapter + `/me`; Google provider/OAuth-client console + real-token e2e in 2.6 |

## AI

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| ADR-0012 | Agent framework spike (ADK vs LangGraph) | Phase 1 | In progress | 1.1 foundation; 1.2 ADK (live); 1.3 LangGraph (live, parity); 1.4 compare |
| — | Confirmed Vertex Gemini model/region (Phase 1.2 live smoke) | Phase 1.2 | ✓ Done | `gemini-2.5-flash` @ `us-central1` (ADC/keyless); `gemini-2.0-flash` 404 in project |
| — | LangGraph adapter parity (same instruction/tool/model as ADK) | Phase 1.3 | ✓ Done | `create_react_agent` + `ChatVertexAI`; live smoke on AAPL |
| F57 | Market-data MCP (yfinance skeleton) | Phase 2.1 | ✓ Done | `get_quote` / `get_fundamentals`; swap to licensed/paid behind MarketDataPort later; India coverage partial |
| ADR-0015 | MCP HTTP microservices (all envs) | Phase 2.2.1 | ✓ Done (market-data) | streamable-HTTP + `/health`; prod = own Cloud Run (2.7); private ingress + token auth later |

## Operational

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| O1 | CI skeleton | Phase 0.1 | ✓ Done | PR #1 |
| O2 | Keyless identity / CD auth | Phase 0.2.3 | ✓ Done | PR #4 |
| O3 | Multi-env | Phase 0 | Partial | In progress |
| O5 | Observability | Phase 0 | Partial | In progress |
| O6 | IaC baseline | Phase 0.3–2.3.1 | Partial → progress | WIF, AR, roles, CD; 2.3.1 APIs + Firestore in TF; rules/indexes + full multi-env later |
| O31 | Verifiable deploys | Phase 0.3.2–0.3.3 | ✓ Done | PR #8, #9 |

## Infrastructure & Technical

| Item | Phase | Status | Notes |
|------|-------|--------|-------|
| Request billing quota increase before creating test/prod projects — billing account at 5-project limit. | Pre-0.2.x | Open | Blocks multi-env projects |
| Terraform state bucket created imperatively (bootstrap); consider `terraform import` later. | 0.2.x | Open | `gs://pcopilot-dev-tfstate` |
| Tighten WIF trust to specific branch/GitHub environment in 0.3 (currently repo-scoped). | 0.3 | Open | Currently `assertion.repository` only |
| Firestore security rules + composite indexes for portfolio queries | Phase 2.x | Open | After StatePort baseline (2.2) |
| Identity Platform Google-provider + OAuth client (console) | Phase 2.6 | Open | Residual manual OAuth; real-token e2e with UI |

## Deferred (seeded)

- **Web framework choice (UI)** — Phase 6
- **Real market-data MCP (licensed/paid provider)** — later; 2.1 yfinance is skeleton only (F57)
- **Agent framework decision** — Phase 1.2–1.4 (ADK vs LangGraph)
