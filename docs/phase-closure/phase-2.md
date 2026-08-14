# Phase 2 — Walking Skeleton — Closure Report

**Status:** Complete · **Closed** 2026-08-14 · **Milestone** M1

## 1. Goal

One thin vertical slice, deployed: a signed-in user can add a holding and get a cited, disclaimed analysis in the browser.

## 2. Exit criteria

| Criterion | Met? | Evidence |
|---|---|---|
| Signed-in user adds a holding and gets a cited, disclaimed analysis, e2e, in staging | Yes | Live e2e 2026-08-14 on https://api-552451662981.asia-south1.run.app — Firebase Google sign-in; NVDA holding saved to Firestore; cited note with market-data MCP citations (`as_of`) + disclaimer. API logs: `POST /portfolios`, `POST /positions`, `POST /analyze`, `GET /me` all 200 (`docs/STATUS.md`). Coordinator-reported analyze ticker: SPCX. |

## 3. Sub-phases / PRs

| Sub-phase | PR | Merged | What landed |
|---|---|---|---|
| 2.1 market-data MCP | [#14](https://github.com/chandranakkalakunta/portfolio-copilot/pull/14) | 2026-08-12 | yfinance `get_quote` / `get_fundamentals` |
| 2.1.1 rename | [#15](https://github.com/chandranakkalakunta/portfolio-copilot/pull/15) | 2026-08-12 | `mcp/` → `mcp_servers/` (avoid PyPI `mcp` shadow) |
| 2.2 Firestore domain | [#16](https://github.com/chandranakkalakunta/portfolio-copilot/pull/16) | 2026-08-12 | Profile / portfolio / position + Firestore + in-memory repos |
| ADR-0015 | [#17](https://github.com/chandranakkalakunta/portfolio-copilot/pull/17) | 2026-08-12 | MCP as HTTP microservices (all envs) |
| 2.2.1 MCP HTTP | [#18](https://github.com/chandranakkalakunta/portfolio-copilot/pull/18) | 2026-08-12 | streamable-HTTP + `/health` + compose |
| 2.3 backend auth | [#19](https://github.com/chandranakkalakunta/portfolio-copilot/pull/19) | 2026-08-12 | AuthPort + Firebase ID-token verify + `/me` |
| 2.3.1 IaC | [#20](https://github.com/chandranakkalakunta/portfolio-copilot/pull/20) | 2026-08-12 | APIs + Firestore in Terraform (plan only at merge; later applied) |
| 2.3.2 CI harden | [#21](https://github.com/chandranakkalakunta/portfolio-copilot/pull/21) | 2026-08-12 | pip-audit, gitleaks, coverage gate 65% |
| 2.3.3 integration | [#23](https://github.com/chandranakkalakunta/portfolio-copilot/pull/23) | 2026-08-13 | Firestore emulator + MCP HTTP tests |
| 2.4 cited note | [#24](https://github.com/chandranakkalakunta/portfolio-copilot/pull/24) | 2026-08-13 | ADK → market-data MCP HTTP → cited note |
| 2.5 API | [#25](https://github.com/chandranakkalakunta/portfolio-copilot/pull/25) | 2026-08-13 | Auth-protected profile / portfolios / positions / analyze |
| 2.6 UI + Google Sign-In | [#26](https://github.com/chandranakkalakunta/portfolio-copilot/pull/26) | 2026-08-14 | Vanilla UI; real-token e2e; Firebase project-id pin |
| 2.7.1 Dockerfile | [#27](https://github.com/chandranakkalakunta/portfolio-copilot/pull/27) | 2026-08-14 | Image bundles `core/` + `adapters/`; CI `docker-build` |
| 2.7.2 runtime IAM | [#28](https://github.com/chandranakkalakunta/portfolio-copilot/pull/28) | 2026-08-14 | run-app roles + `mcp-run` SA (applied & verified 2026-08-14) |
| 2.7.3 deploy prep | [#29](https://github.com/chandranakkalakunta/portfolio-copilot/pull/29) | 2026-08-14 | Lazy ADK/LangGraph/Vertex imports; MCP ID-token auth |
| 2.7.4 deploy | [#30](https://github.com/chandranakkalakunta/portfolio-copilot/pull/30) | 2026-08-14 | Two Cloud Run services: `api` (public) + `market-data-mcp` (private) |
| Doc-hygiene | [#31](https://github.com/chandranakkalakunta/portfolio-copilot/pull/31) | 2026-08-14 | Reconcile backlog/STATUS; close Phase 2 |

Also: README hygiene PR [#22](https://github.com/chandranakkalakunta/portfolio-copilot/pull/22) (2026-08-12).

## 4. Key decisions & ADRs

- **ADR-0003** — display-only / no real execution (re-checked on the UI + analyze path).
- **ADR-0005** — MCP server boundaries; **transport superseded by ADR-0015** (HTTP microservices in all envs).
- **ADR-0006** — reviewer agent: **partial** (not built; Phase 4).
- Firebase Auth lives in project `pcopilot-dev-d0a08`; Firestore/Vertex use `pcopilot-dev`. Token verification is pinned to `PCOPILOT_FIREBASE_PROJECT_ID`.
- Public API Cloud Run needs `roles/run.admin` on `gh-deployer` (`setIamPolicy` for `allUsers`) — caught in PR #30 review.
- Staging DRS exception: `iam.allowedPolicyMemberDomains` = `allowAll:true` on `pcopilot-dev` (2026-08-14).

## 5. Requirements covered

- **F58** Google Sign-In (backend + real-token e2e).
- **F5 / F6** manual holding / profile store (StatePort) — domain + API + live write; security rules / indexes later.
- **F40–F42 / F57** market-data MCP (yfinance skeleton; HTTP).
- **F17 / F25–F27** cited fundamental note (disclaimer + as-of sources) — one agent; full engine is Phase 4.
- **F45 / F46** minimal UI + attribution/disclaimer (skeleton; full dashboard Phase 6).
- **O8 / O10 / O11** integration tests, dep/secret scan, coverage — in progress as ongoing gates.

## 6. Deferrals carried forward

From `docs/backlog.md` (still Open):

- Delete stale Cloud Run service `hello`.
- Re-tighten project DRS after staging (prod: LB+NEG).
- Tighten `roles/run.invoker` from project-scoped to the MCP service.
- Re-tighten `gh-deployer` from `run.admin` to `run.developer` + service-scoped invoker management.
- Firestore security rules + composite indexes.
- GET foreign portfolio **403 → 404** (privacy; existence leak).
- Pre-auth UI cosmetic: “Database is closing/hidden” before sign-in (Phase 6).
- Web framework choice remains Phase 6.

## 7. Verification

- Hermetic CI (lint, mypy, unit, coverage, pip-audit, gitleaks) + integration job + `docker-build`.
- Local smoke: `scripts/spike_fundamental_note.py` against localhost MCP (token-free `http://`).
- Live staging 2026-08-14: Google sign-in, NVDA holding persisted, cited note rendered, disclaimer shown. URL: https://api-552451662981.asia-south1.run.app

## 8. Learnings

- [0001](../learnings/0001-prompt-fidelity-spectrum.md) — prompt fidelity spectrum (2.7.4 retro).
- [0002](../learnings/0002-public-cloud-run-needs-run-admin.md) — public Cloud Run needs `run.admin`.
- [0003](../learnings/0003-drs-exception-allowall.md) — DRS exception for staging public ingress.
- [0004](../learnings/0004-plan-only-iac-drifts.md) — plan-only IaC drifts from reality.
- [0005](../learnings/0005-adc-restart-required.md) — ADC expiry requires a full API process restart.
