# Architecture Decision Records (ADRs)

This directory holds the Architecture Decision Records for Portfolio Copilot. An ADR documents a decision with genuine alternatives, made with awareness of trade-offs, that future contributors need to understand to maintain the system (per Multi-Agent Engineering Protocol v4.0, §7.1, §7.5). ADRs are immutable once Accepted — supersede with a new ADR rather than editing.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-hexagonal-architecture.md) | Adopt hexagonal (ports & adapters) architecture | Accepted |
| [0002](0002-gcp-initial-cloud.md) | GCP as the initial cloud, portability preserved | Accepted |
| [0003](0003-display-only-boundary.md) | Display-only / no real-execution safety boundary | Accepted |
| [0004](0004-datastore-split.md) | State + analytical store split (Firestore + BigQuery) & data model | Accepted |
| [0005](0005-mcp-boundaries-transport.md) | MCP server boundaries and transport | Accepted |
| [0006](0006-runtime-reviewer-agent.md) | Runtime reviewer agent (propose→review→gate) | Accepted |
| [0007](0007-caching-cost-budget.md) | Caching strategy and cost-budget policy | Accepted |
| [0008](0008-prompt-injection-guardrails.md) | Prompt-injection / guardrail approach for ingested content | Accepted |
| [0009](0009-keyless-identity.md) | Keyless identity (WIF for CI, ADC / SA-impersonation at runtime) | Accepted |
| [0010](0010-multi-market-conventions.md) | Multi-market conventions (US + India, benchmarks, TWR/MWR) | Accepted |
| [0011](0011-tech-stack-baseline.md) | Technology stack baseline (open-source / free-first) | Accepted |
| [0012](0012-agent-framework-selection.md) | Agent framework selection (ADK vs LangGraph) | Proposed — pending spike |
| [0013](0013-environment-isolation.md) | Environment isolation via separate GCP projects | Accepted |
| [0014](0014-backend-web-framework.md) | Backend web framework — FastAPI | Accepted |

## Status legend

- **Proposed** — under consideration; decision not yet made (e.g., awaiting a spike).
- **Accepted** — decided and in force.
- **Superseded by ADR-XXXX** — replaced; see the newer ADR.
- **Deprecated** — no longer applies.

## Conventions

- Filenames: `NNNN-short-title.md`, zero-padded sequential numbers.
- Each ADR: Status, Context, Decision, Consequences, Alternatives considered.
- New decisions during implementation get the next number and land with the PR that makes the decision (protocol §7.5). More ADRs will be added as phases proceed.
