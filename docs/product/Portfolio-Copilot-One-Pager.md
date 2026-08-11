# Portfolio Copilot — Project One-Pager

**An AI equity-research analyst that knows your portfolio.** Built on an agentic framework (Google ADK) and MCP, it takes a user's profile and holdings and produces cited, personalized buy / sell / trim ideas — for both existing positions and new stocks — across US and Indian markets.

*Not investment advice. All outputs are informational; the user is solely responsible for their own due diligence and decisions.*

---

## The problem

Retail investors drown in data but lack a personal analyst. The hardest decision isn't *"is this a good company?"* — it's *"given what I already hold, my risk tolerance, and my market, should I buy this, add to it, trim it, or sell it?"* Generic stock tools ignore the user's actual portfolio context. That rebalancing judgment is exactly where a multi-agent system adds value.

## The concept

A user connects or enters a profile — preferred stock types, risk profile, current holdings, target market (US or India), and whether they want *new* ideas or a verdict on *existing* positions (trim / add / hold / sell). A team of specialist agents analyzes each candidate on a common framework, scores it **relative to the existing portfolio** (concentration, sector overlap, correlation, risk budget), and returns a ranked set of ideas — each backed by a cited research note. Data is pulled fresh on demand when the user asks.

The "sell from portfolio ↔ buy new ideas" symmetry is the core hook: buy and sell candidates are scored on the same rubric and ranked against each other, which mirrors the real rebalancing decision.

## User inputs (profile)

- **Market:** US or India (drives data sources, tickers, currency, disclosures)
- **Interests:** sectors / themes / stock types the user cares about
- **Risk profile:** conservative → aggressive; position-sizing and volatility tolerance
- **Current portfolio:** holdings, weights, cost basis (uploaded or connected)
- **Intent:** discover new ideas, or evaluate existing holdings (trim / add / hold / sell)

## How it works (agentic architecture)

An **orchestrator** plans the analysis and coordinates specialist sub-agents:

- **Fundamental analyst** — financials, ratios, peer comparison
- **Technical analyst** — price / volume, momentum, trend
- **Sentiment & filings analyst** — news, analyst ratings, SEC/EDGAR & Indian filings, earnings calls
- **Risk analyst** — volatility, drawdown, macro/sector exposure; devil's-advocate pass
- **Portfolio-fit analyst** *(the differentiator)* — scores each candidate against the user's actual holdings and risk budget
- **Report writer** — synthesizes a rating and a cited research note

**Tooling via MCP:** each data source is an MCP server the agents call — market data (near-real-time), filings, news, and *paper* trading (simulated only, never live execution). Some servers are off-the-shelf; 1–2 built in-house become strong portfolio artifacts.

## Tech stack

- **Now — GCP-centric:** Gemini on Vertex AI, BigQuery (holdings, time-series, backtest results), Cloud Run (service), Firestore (user state).
- **Future — cloud-agnostic:** clean separation between the agent/MCP layer and infrastructure, so LLM provider, data store, and hosting can be swapped. MCP and the agent framework stay portable; cloud services sit behind interfaces.
- **Interface:** web dashboard — watchlist + holdings, ranked buy/sell ideas, drill-down cited notes.

## Monitoring & paper trading

Two distinct, related capabilities:

- **Recommendation tracking (core).** Every buy/sell/trim idea is logged with a timestamp and the price at issue, then scored against actual forward returns — producing an auditable *track record* and doubling as the evaluation harness. Runs whether or not the user "trades," because it only scores the agent's outputs against market data over time.
- **Paper trading (optional layer).** A simulated portfolio the user can act on: ideas execute as virtual buys/sells, positions and cash update, P&L is tracked as if real. **US** via a paper-trading broker sandbox (e.g., Alpaca); **India** via internal fill simulation on live/EOD prices (true broker paper APIs are thin). Simulated only — never live-money execution.

## What makes it production-grade

Evaluation harness (score the agent's calls against real forward returns), tracing/observability, on-demand data with a caching layer to control cost and latency, guardrails and mandatory disclaimers, and human-in-the-loop before any paper trade.

## Guardrails & positioning

Analysis and paper trading only — **never live execution** on the user's behalf. This keeps the product legal without RIA/SEC registration. Every recommendation is cited and auditable. All outputs carry a clear "not financial advice — do your own due diligence" statement.

## Startup-seed differentiators

Portfolio-aware personalization, fully cited/auditable research, and multi-market (US + India) coverage — a combination retail tools handle poorly.

---

## Related documents

| Document | Path | Status |
|---|---|---|
| Detailed requirements | [`docs/requirements/Portfolio-Copilot-Requirements.md`](../requirements/Portfolio-Copilot-Requirements.md) | Draft v0.2 |
| Architecture | `docs/architecture/` | Planned |
| Design | `docs/design/` | Planned |
| ADRs | `docs/adr/` | Planned |
| Implementation phases | (roadmap; location TBD) | Planned |
