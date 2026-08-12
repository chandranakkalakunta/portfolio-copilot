# ADR-0001: Adopt hexagonal (ports & adapters) architecture

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F54–F57, NFR Deployment; architecture §6

## Context

Portfolio Copilot is GCP-native for v1 but must become cloud-agnostic, and every module (agents, MCP servers, stores, model/data providers) must be pluggable in/out without rewriting the rest (F54–F57). If core domain logic imports cloud or provider SDKs directly, portability and modularity become aspirational rather than real, and a later cloud move turns into a rewrite.

## Decision

Adopt a **hexagonal (ports & adapters)** architecture. The application core (domain + services: analysis orchestration contracts, valuation, tracking, policy) depends only on **ports** — interfaces the core defines. Concrete **adapters** implement each port for a specific provider or cloud. No cloud/provider SDK is imported by core logic; it appears only inside adapters. Primary ports: `AgentFrameworkPort`, `LLMPort`, `MarketDataPort`, `FilingsPort`, `NewsPort`, `StatePort`, `TimeSeriesPort`, `CachePort`, `QueuePort`, `SecretsPort`, `BlobPort`.

## Consequences

**Positive:** swapping a provider or cloud is an adapter change, not a core rewrite (F55); modules are independently testable and replaceable (F54); the open-source-first → paid upgrade path is a config/adapter change (F57); portability is demonstrable, not claimed (F56).

**Negative / cost:** one extra layer of indirection; interfaces must be designed and maintained; risk of leaky abstractions if a provider-specific concept bleeds into a port.

**Follow-ups:** keep at least one alternate adapter for `LLMPort` and a store port to prove portability (F56); lint/CI check that core packages do not import cloud SDKs.

## Alternatives considered

- **Direct SDK usage in core (no ports).** Simpler and faster initially, but couples the system to GCP/providers and violates F54–F57; rejected.
- **Full microservices from day one.** Over-engineered for v1 scale; deployment topology is handled separately (containers per component) without forcing service boundaries into the domain model.
