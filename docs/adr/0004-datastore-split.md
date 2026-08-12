# ADR-0004: State + analytical store split (Firestore + BigQuery) and core data model

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F6, F10–F16, F29–F32, NFR Scalability; architecture §9; behind ADR-0001 ports

## Context

The system has two distinct data shapes: low-latency **operational state** (users, profiles, portfolios, positions) read constantly by the dashboard, and high-volume **time-series/analytical** data (valuation snapshots, recommendations, forward-return scores, eval sets, traces) that grows without bound and is queried analytically. A single store optimized for one is poor at the other, and the design must scale toward millions of users.

## Decision

Split persistence by access pattern, both behind ports (ADR-0001): **`StatePort` → Firestore** for operational state (per-user isolation, fast document reads), and **`TimeSeriesPort` → BigQuery** for analytical/time-series data (valuations, recommendations, scores, eval, traces). Core entities: User, Profile, Portfolio, Position, ValuationSnapshot, PaperTrade, Recommendation, ForwardScore, ResearchNote (see architecture §9 ER model). Exported artifacts go to `BlobPort` (GCS).

## Consequences

**Positive:** each workload uses a fit-for-purpose store; analytical queries and charts scale cheaply on BigQuery; operational reads stay fast and isolated; both swappable via ports (Postgres/ClickHouse alternates).

**Negative / cost:** two stores to operate; some data (e.g., latest valuation) is duplicated between operational and analytical layers and must be kept consistent; eventual-consistency care on writes that fan out.

**Follow-ups:** define the write path for valuations (operational latest + analytical history); document retention windows per market (open item).

## Alternatives considered

- **Single relational DB (Postgres) for everything.** Simpler ops, but weaker at large-scale append-only analytical/time-series workloads and per-document hot-state reads at target scale; remains the documented alternate adapter.
- **Single document DB for everything.** Poor analytical querying for track-record/eval; rejected.
