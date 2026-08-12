# ADR-0009: Keyless identity (WIF for CI, ADC / SA-impersonation at runtime)

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements NFR Security, F41; architecture §13; engineering protocol §4.8, §5.13

## Context

The system needs credentials for CI/CD and for runtime access to GCP services and provider APIs. Long-lived JSON service-account keys are a persistent leak and rotation liability, and the engineering protocol mandates zero JSON service-account keys (§4.8). Provider keys must also stay isolated inside MCP servers (F41).

## Decision

Use **keyless identity** everywhere: **Workload Identity Federation (WIF)** for CI/CD (no exported keys), **Application Default Credentials (ADC)** for local development, and **service-account impersonation** for runtime access that requires OAuth2 tokens. Provider API keys (market data, news, etc.) live only in **Secret Manager** (`SecretsPort`) and are read by the MCP servers, never exposed to the agent/LLM layer. IAM follows least-privilege, discovered by loud failures rather than pre-granting broad roles (protocol §4.11). Impersonation chains grant IAM to the impersonated identity, not the caller (protocol §5.13).

## Consequences

**Positive:** no long-lived keys to leak or rotate; auditable, minimal IAM; provider secrets isolated; aligns with GCP "secure by default".

**Negative / cost:** more setup effort (WIF, impersonation) than dropping in a key; occasional ADC re-auth friction (protocol §5.10, §5.22); least-privilege discovery takes iterations.

**Follow-ups:** codify all IAM in Terraform (nothing granted only imperatively, protocol §5.32); document the alternate-cloud identity approach for portability.

## Alternatives considered

- **JSON service-account keys.** Simplest, but forbidden by protocol §4.8 and a standing security risk; rejected.
- **Broad pre-granted roles (Editor).** Faster, but produces over-permissioned principals and audit findings; rejected in favor of least-privilege discovery.
