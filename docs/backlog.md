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
| O1–O6 | Repo scaffolding, pinned toolchain (py3.12/uv/ruff/mypy/pytest), CI skeleton | Phase 0.1 | In progress | This PR |
| F55 | No cloud SDK in `core/` (guard test) | Phase 0.1 | In progress | ADR-0001 |
| — | GCP projects + keyless WIF | Phase 0.2 | Deferred | ADR-0009; no cloud resources in 0.1 |
| — | Terraform IaC baseline | Phase 0.3 | Deferred | dev/staging IaC after identity rails |

## Deferred (seeded)

- **Web framework choice** — Phase 6
- **Terraform IaC baseline** — Phase 0.3
- **GCP projects + keyless WIF** — Phase 0.2
