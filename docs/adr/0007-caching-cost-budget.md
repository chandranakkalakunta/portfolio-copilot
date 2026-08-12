# ADR-0007: Caching strategy and cost-budget policy

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F38, F39, A3, NFR Cost control; architecture §13, §15

## Context

The product provides near-real-time data on request and runs multi-agent analysis that calls paid data and LLM APIs repeatedly. Without caching and budgets, a single analysis can hit the same market-data endpoint many times and burn LLM tokens unpredictably, blowing up cost and latency — a real risk at target scale.

## Decision

Make **caching mandatory** and **cost a first-class, tracked metric**. Two cache tiers behind `CachePort`: (1) a **market-data cache** in each MCP server keyed by symbol+field+as-of window, and (2) an **analysis-result cache** for recent identical requests. Every cached value carries a **data-as-of** marker surfaced in the UI (F39) — freshness is never overstated. Enforce **per-request token/cost budgets** with model-tier selection by depth (quick vs deep, F24, A3); record per-request tokens, tool calls, latency, and cost in traces (analytical store, ADR-0004). Cache TTLs are configurable per data type (intraday vs fundamentals vs filings).

## Consequences

**Positive:** bounded provider and LLM spend; lower tail latency; freshness honesty; cost observability enables tuning.

**Negative / cost:** cache-invalidation complexity; risk of serving stale data if TTLs are wrong (mitigated by as-of markers and per-type TTLs); added infrastructure (Memorystore in prod).

**Follow-ups:** define TTLs per data type; set default per-request budget and alerting thresholds; dashboards for cache-hit and cost.

## Alternatives considered

- **No caching, always fetch fresh.** Simpler and maximally fresh, but cost/latency untenable at scale; rejected (caching is a requirement, not optional).
- **Single global cache tier.** Less effective than per-domain + result caching; the two-tier split targets the two distinct hot paths.
