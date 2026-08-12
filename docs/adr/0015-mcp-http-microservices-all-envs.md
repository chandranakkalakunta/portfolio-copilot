# ADR-0015: MCP servers run as HTTP microservices in all environments

- **Status:** Accepted (2026-08-12)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** supersedes the *transport* decision in ADR-0005; requirements F40–F43, F54, O31; engineering-protocol §5.31, §5.32 (env-parity failures); architecture §8

## Context

ADR-0005 chose per-domain MCP servers with **stdio transport in dev** and **HTTP in prod**. That split means dev and prod exercise different transports, connection handling, and failure modes — precisely the environment divergence that produces "works in dev, breaks in prod" bugs that are hardest to debug where it hurts most (protocol §5.31 mocked/local ≠ real; §5.32 config/behavior doesn't travel). The Coordinator asked to eliminate this divergence even though it costs more up front.

## Decision

**MCP servers run as standalone HTTP microservices (streamable-HTTP/SSE) in ALL environments** — local dev, test, and prod. Agents connect to them as HTTP MCP clients using a per-server URL from configuration (e.g. `MARKET_DATA_MCP_URL`). Each server is containerized, listens on `$PORT`, and exposes a `/health` endpoint carrying build ID + deploy time (O31). Locally the server runs as its own process/container (optionally via docker-compose); in prod it is its own Cloud Run service. This makes every environment structurally identical.

What is **unchanged** from ADR-0005: per-domain server boundaries, provider-key isolation inside each server, caching, and semantic error mapping. Only the transport (no longer stdio-in-dev) is superseded.

## Consequences

**Positive:** true dev/prod parity — the agent↔MCP boundary behaves identically everywhere; independent deploy/scale per server from day one (F43); env-specific transport bugs are surfaced locally, not in prod.

**Negative / cost:** more moving parts locally (each MCP server is a running service, not an in-process import); service URLs and startup/orchestration must be managed (compose or a run recipe); slightly slower local iteration. Accepted deliberately for the parity benefit.

**Follow-ups:** containerize each MCP server; add `/health` (O31) to each; wire agents via HTTP MCP client with configurable URLs; deploy each MCP server as its own Cloud Run service; provider keys via Secret Manager per service.

## Alternatives considered

- **Keep ADR-0005's stdio-dev / HTTP-prod split.** Simpler local iteration, but reintroduces the environment divergence this ADR exists to remove; rejected on the Coordinator's parity requirement.
- **stdio everywhere (co-locate as subprocess in all envs).** Uniform, but doesn't match how independently-scaled services actually run in prod and blocks per-server scaling; rejected.
