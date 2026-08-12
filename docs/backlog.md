# Project Backlog

Traceability of functional (F#), AI (A#), and operational (O#) requirements to implementation phases/PRs per Multi-Agent Engineering Protocol v4.0 (§7.7).

## Functional

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| — | Web framework choice | Phase 6 | Deferred | UI stack selection deferred until product shell phase |

## AI

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| — | — | — | — | Seeded at Phase 0.1; populate as spikes open |

## Operational

| ID | Item | Phase | Status | Notes |
|----|------|-------|--------|-------|
| O1–O6 | Repo scaffolding, pinned toolchain (py3.12/uv/ruff/mypy/pytest), CI skeleton | Phase 0.1 | Done | PR #1 |
| F55 | No cloud SDK in `core/` (guard test) | Phase 0.1 | Done | ADR-0001 |
| — | Keyless WIF pool/provider + deployer SA (Terraform, plan only) | Phase 0.2.2 | In progress | ADR-0009; no apply until Strategist review |
| — | Terraform IaC baseline (deploy roles, Cloud Run, etc.) | Phase 0.3 | Deferred | After WIF apply |
| — | Web framework choice | Phase 6 | Deferred | UI stack selection deferred until product shell phase |

## Infrastructure & Technical

| Item | Phase | Status | Notes |
|------|-------|--------|-------|
| Request billing quota increase before creating test/prod projects — billing account at 5-project limit. | Pre-0.2.x | Open | Blocks multi-env projects |
| Terraform state bucket created imperatively (bootstrap); consider `terraform import` later. | 0.2.x | Open | `gs://pcopilot-dev-tfstate` |
| Tighten WIF trust to specific branch/GitHub environment in 0.3 (currently repo-scoped). | 0.3 | Open | Currently `assertion.repository` only |

## Deferred (seeded)

- **Web framework choice** — Phase 6
- **Terraform IaC baseline** — Phase 0.3
- **GCP projects + keyless WIF** — Phase 0.2.2 (plan); apply after review
