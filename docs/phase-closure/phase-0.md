# Phase 0 — Foundations & Rails — Closure Report

**Status:** Complete · **Closed** 2026-08-12 · **Milestone** M1

## 1. Goal

Stand up the production-grade skeleton before any product feature: monorepo, CI/CD, environments, keyless identity, hexagonal scaffolding, and a verifiable deploy.

## 2. Exit criteria

| Criterion | Met? | Evidence |
|---|---|---|
| Trivial service builds in CI and deploys via keyless CD | Yes | CI on every PR; deploy-on-merge CD via WIF (PR #4 identity check; PR #9 CD). Cloud Run service `hello` (PR #8). |
| No cloud SDK in `core/` (CI-guarded) | Yes | Guard test + F55; PR #1. |
| Rollback verified | (not recorded) | Required by the phase roadmap; no rollback drill or evidence is in CHANGELOG, backlog, or PR history. |

## 3. Sub-phases / PRs

| Sub-phase | PR | Merged | What landed |
|---|---|---|---|
| 0.1 scaffolding | [#1](https://github.com/chandranakkalakunta/portfolio-copilot/pull/1) | 2026-08-12 | Repo skeleton, Python 3.12 / uv / ruff / mypy, `core/ports`, CI |
| 0.1.1 gitignore | [#2](https://github.com/chandranakkalakunta/portfolio-copilot/pull/2) | 2026-08-12 | `.gitignore`; remove committed bytecode |
| 0.2.2 WIF | [#3](https://github.com/chandranakkalakunta/portfolio-copilot/pull/3) | 2026-08-12 | WIF pool/provider + deployer SA (plan only) |
| 0.2.3 keyless auth | [#4](https://github.com/chandranakkalakunta/portfolio-copilot/pull/4) | 2026-08-12 | GitHub Actions OIDC → WIF → SA check |
| 0.3.1 deploy infra | [#7](https://github.com/chandranakkalakunta/portfolio-copilot/pull/7) | 2026-08-12 | Artifact Registry + runtime SA + scoped deployer roles (plan only) |
| 0.3.2 hello service | [#8](https://github.com/chandranakkalakunta/portfolio-copilot/pull/8) | 2026-08-12 | FastAPI `/health` `/ready` `/version` + Dockerfile (O31) |
| 0.3.3 CD | [#9](https://github.com/chandranakkalakunta/portfolio-copilot/pull/9) | 2026-08-12 | Deploy-on-merge to Cloud Run via WIF |

Related docs PRs in the same window: ADR-0013 / ADR-0014 / requirements v0.4 ([#5](https://github.com/chandranakkalakunta/portfolio-copilot/pull/5), [#6](https://github.com/chandranakkalakunta/portfolio-copilot/pull/6)).

## 4. Key decisions & ADRs

- **ADR-0001** — hexagonal (ports & adapters); cloud SDKs stay out of `core/`.
- **ADR-0002** — GCP as the initial cloud; portability preserved.
- **ADR-0009** — keyless identity (WIF for CI; ADC / SA impersonation at runtime). No SA keys.
- **ADR-0011** — tech-stack baseline (Python, open-source / free-first).
- **ADR-0013** — environment isolation via separate GCP projects.
- **ADR-0014** — FastAPI as the backend web framework.

## 5. Requirements covered

- **O1** CI (lint, type-check, unit) — PR #1.
- **O2** Keyless CD identity proven — PR #4.
- **O3 / O5 / O6** environments, observability, IaC — **partial** (rails started; not closed).
- **O31** verifiable deploys (`build_id` + `deployed_at`) — PRs #8, #9.
- **F55** no cloud SDK in `core/` — PR #1.

## 6. Deferrals carried forward

- Terraform state bucket created imperatively (`gs://pcopilot-dev-tfstate`); consider `terraform import` later.
- WIF trust is repo-scoped (`assertion.repository` only), not branch/environment-tightened.
- Multi-env projects blocked on billing-account project quota (5-project limit) — (recorded in backlog).
- Observability baseline (O5) and full IaC/multi-env (O3/O6) remain open.

## 7. Verification

CI green on `main`. Keyless auth-check workflow exercises WIF. `hello` deployed to Cloud Run in `pcopilot-dev` / `asia-south1` (later superseded by the Phase 2 `api` service). Rollback drill: (not recorded).

## 8. Learnings

None specific to Phase 0 in `docs/learnings/` yet. Later: [0004](../learnings/0004-plan-only-iac-drifts.md) (plan-only IaC drift) applies to 0.2.2 / 0.3.1 plan-only Terraform.
