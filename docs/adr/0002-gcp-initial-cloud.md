# ADR-0002: GCP as the initial cloud, portability preserved

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements NFR Deployment, F55–F56; architecture §14; depends on ADR-0001

## Context

The team is GCP-centric and wants first-class access to Gemini/Vertex AI. The product must still be cloud-agnostic in architecture (F55–F56). We need a concrete initial platform to build on without foreclosing a future move.

## Decision

Use **Google Cloud Platform** as the v1 platform: Cloud Run (app, BFF, MCP servers), Vertex AI/Gemini (`LLMPort`), Firestore (`StatePort`), BigQuery (`TimeSeriesPort`), Memorystore (`CachePort`), Pub/Sub + Cloud Scheduler (`QueuePort`), Secret Manager (`SecretsPort`), GCS (`BlobPort`), Cloud Logging/Monitoring/Trace. Every service is consumed through the ports defined in ADR-0001, so GCP is an adapter set, not a hard dependency.

## Consequences

**Positive:** native Gemini/Vertex integration; managed, autoscaling, low-ops services; team familiarity; free tiers support the open-source/free-first goal.

**Negative / cost:** GCP-specific operational knowledge required; must actively prevent GCP SDKs leaking into core (enforced by ADR-0001).

**Follow-ups:** maintain a documented alternate-adapter mapping (e.g., AWS: Fargate + Bedrock + DynamoDB + S3 + SQS) as portability proof (F56).

## Alternatives considered

- **AWS / Azure.** Viable, but no advantage for this team and weaker fit with the chosen Gemini-first model strategy; portability is preserved regardless via ADR-0001, so this is reversible.
- **Cloud-neutral from day one (multi-cloud).** Higher cost and complexity for no v1 benefit; the ports approach already keeps the door open.
