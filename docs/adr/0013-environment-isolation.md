# ADR-0013: Environment isolation via separate GCP projects

- **Status:** Accepted (2026-08-12)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements O5 (environments), NFR Security/Deployment; ADR-0002 (GCP), ADR-0009 (keyless identity); realized in Phase 0.2

## Context

The system needs isolated environments for development, testing, and production. Isolation can be achieved at different granularities: separate resources/namespaces within one cloud project, or a separate project per environment. The choice affects IAM blast radius, quota/billing isolation, and how cleanly environment-specific policies can be applied. The decision must be made intentionally rather than by default, because it shapes all later infrastructure.

## Decision

Use a **separate GCP project per environment**: `pcopilot-dev`, `pcopilot-test`, `pcopilot-prod`. Each project has its own IAM, quotas, service accounts, WIF configuration, and (where applicable) billing association. Pragmatic sequencing: **`pcopilot-dev` is created first** (Phase 0.2); `test` is added when continuous-delivery promotion is wired; `prod` near GA — so empty environments are not stood up before they are needed.

## Consequences

**Positive:** strong isolation — a mistake, over-permission, or runaway cost in dev cannot affect prod; per-environment org policies and quotas; clean, auditable IAM per project; keyless WIF trust scoped per environment (ADR-0009).

**Negative / cost:** more setup and some cross-project plumbing (e.g., Artifact Registry sharing or per-project registries); billing-account **project-quota pressure** — the billing account is currently at its 5-project limit, so a **billing quota increase must be requested before `test`/`prod` are created** (logged in `docs/backlog.md`).

**Follow-ups:** request the billing quota increase before Phase-later env creation; replicate the Phase 0.2 WIF/SA Terraform per environment; parameterize `infra/` by environment (project_id/number/region) when `test` lands.

## Alternatives considered

- **Single project with resource/namespace separation (env prefixes, separate service accounts).** Cheaper and simpler plumbing, but weak isolation — shared IAM surface and quotas, higher blast radius, and easy to accidentally cross environments. Rejected for a product intended to reach production and internet scale.
- **Separate projects AND separate folders/orgs per environment.** Stronger still, but unnecessary overhead at this stage; can be layered on later within the same org if governance needs grow.
