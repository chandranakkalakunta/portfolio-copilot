# ADR-0003: Display-only / no real-execution safety boundary

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements §3, §11, F7, F33–F35, F51; architecture §2, §8

## Context

The product analyzes stocks, tracks portfolios, and offers paper trading. Executing real trades or moving real money would create significant regulatory exposure (US RIA/SEC; India SEBI investment-adviser rules) and liability. The user has decided the product must **never** trade real money — real holdings are tracked read-only for display, and paper trading is simulated only.

## Decision

Establish **display-only** as an architectural invariant. No component may place, route, or convert-into-real any order. Specifically: real-holdings ingestion and any broker/aggregator connection are **read-only scopes only** (F7, F8); paper trading is **simulated only** with no code path to real execution (F33–F35); outputs never contain execution instructions or return guarantees (F51). This boundary is enforced in the paper-trading MCP (no real-order capability exists) and in guardrails/policy.

## Consequences

**Positive:** avoids RIA/brokerage registration and money-movement risk; keeps disclaimers truthful; simplifies compliance and security scope.

**Negative / cost:** cannot offer real order execution as a feature; users must transact elsewhere. Accepted deliberately.

**Follow-ups:** CI/guardrail check that no adapter exposes a real-order method; disclaimers surfaced on every recommendation and performance view (F49).

## Alternatives considered

- **Allow real execution (now or later).** Rejected for v1: triggers registration, custody, and liability concerns disproportionate to the product's value, which is analysis and tracking. A future reversal would require its own ADR and a compliance program.
- **Real execution via a licensed partner.** Out of scope; revisit only if the product pivots to brokerage.
