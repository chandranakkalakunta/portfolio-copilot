# ADR-0005: MCP server boundaries and transport

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F40–F44, F41, F42; architecture §8

## Context

Agents need external data (market data, filings, news, paper trading). We must decide how these are exposed to the agents, how they are bounded, and how they run in dev vs prod. Poor boundaries (one monolith tool server) couple unrelated concerns and prevent independent scaling; leaking provider keys to the agent/LLM layer is a security risk.

## Decision

Expose data sources as **four focused, per-domain MCP servers**: **Market-data**, **Filings** (normalized across SEC EDGAR and BSE/NSE/SEBI), **News/Sentiment**, and **Paper-trading** (simulated only). Each server: owns its provider credentials internally (`SecretsPort`), never exposing them to agents (F41); enforces caching, rate-limiting, and semantic error mapping (F42; protocol §5.15, §5.24). **Transport:** stdio (local subprocess) in dev; HTTP/SSE as an independently deployable Cloud Run service in prod (F43). The user's own portfolio/profile data is **not** an MCP server — it is accessed directly by internal services.

## Consequences

**Positive:** independent deploy/scale/failure per domain; clean security boundary for keys; reusable servers (the Filings server is a custom, portable artifact, F44); dev/prod parity via one transport switch.

**Negative / cost:** more deployable units to operate; a shared cross-cutting fix must be applied per server.

**Follow-ups:** define each server's tool schemas and error taxonomy; contract tests per server (risk-sensitive per protocol §3.5).

## Alternatives considered

- **Single monolithic tool server.** Simpler to deploy but couples domains, blocks independent scaling, and widens the blast radius of a key or failure; rejected.
- **Direct in-process tool functions (no MCP).** Loses reusability, language-agnosticism, and the security boundary; MCP also serves the cloud-agnostic goal. Acceptable only for the internal portfolio store, which is not MCP.
