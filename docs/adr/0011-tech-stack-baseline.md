# ADR-0011: Technology stack baseline (open-source / free-first)

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements Goals, F57, Constraints; architecture §17; complements ADR-0002 (cloud), ADR-0004 (stores), ADR-0012 (framework)

## Context

We need a baseline technology stack for v1 that lets us validate cheaply and swap providers later without a rewrite. This ADR records the stack-wide baseline and the free-first principle; it deliberately does **not** re-decide cloud (ADR-0002), stores (ADR-0004), or agent framework (ADR-0012) — it references them, to keep each decision focused (protocol §7.5).

## Decision

Adopt an **open-source / free-first** baseline, everything behind ADR-0001 ports so upgrades are config/adapter changes (F57):

- **Language/runtime:** Python for agents, services, and MCP servers (strong AI/data ecosystem, ADK & LangGraph support).
- **Models:** Gemini free tier / local OSS models in dev; Grok for the runtime reviewer (behind `LLMPort`); paid tiers later.
- **Market data & filings:** yfinance / Alpha Vantage free tier; SEC EDGAR + NSE/BSE public data; paid vendors later.
- **Web/PWA:** a modern JS/TS framework delivering an installable PWA (F53); specific choice finalized in the UI phase.
- **IaC & CI:** Terraform; keyless CI via WIF (ADR-0009).
- **Testing/eval:** unit/integration tests plus an eval harness for the non-deterministic analysis engine (A1).
- **Toolchain versions pinned explicitly** at project creation (protocol §5.23).

## Consequences

**Positive:** low/zero cost to validate; broad ecosystem; portability preserved; clear upgrade path to paid providers without consumer code change.

**Negative / cost:** free tiers have rate/coverage limits (especially India data) that may force earlier paid upgrades; multiple pluggable options add configuration surface.

**Follow-ups:** finalize the web/PWA framework in the UI phase (may warrant its own ADR); pin exact versions in `pyproject`/`package.json`/`.python-version`.

## Alternatives considered

- **Premium data/models from day one.** Better coverage/quality, but cost before validation; deferred until the concept is proven.
- **Polyglot core (Go/Java services).** Python's AI/data ecosystem and framework support outweigh performance gains at this stage; MCP servers could still be written in another language later behind their contracts.
