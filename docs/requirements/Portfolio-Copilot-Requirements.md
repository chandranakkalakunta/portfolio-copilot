# Portfolio Copilot — Requirements

**Document:** Detailed Product Requirements
**Version:** 0.2 (draft)
**Last updated:** 11 August 2026
**Status:** Draft for review
**Change log:** v0.2 — added PWA (F53); modularity/pluggability as a first-class implementation requirement (§6.12, F54–F56); explicit internet-scale scalability to millions of users (NFR, now P0); open-source/free-first sourcing principle (Goals, Constraints).
**Related documents:** Project One-Pager (`docs/product/Portfolio-Copilot-One-Pager.md`); Technical Architecture (`docs/architecture/Portfolio-Copilot-Architecture.md`, v0.1); Multi-Agent Engineering Protocol v4.0 (`chandra-prompts/`); Design notes (`docs/design/`, to be written); ADRs (`docs/adr/`, 0001–0012).

> **Positioning & disclaimer.** Portfolio Copilot is an informational research and portfolio-tracking product. It is **display-only**: it never executes real trades and never moves real money. All outputs are informational and are **not investment advice**; the user is solely responsible for their own due diligence and decisions.

---

## 1. Overview

Portfolio Copilot is an AI equity-research analyst that understands a user's own portfolio. Given a user profile (interests, risk tolerance, holdings, target market) it produces cited, personalized ideas — buy / add / hold / trim / sell — for both existing positions and new stocks, across US and Indian markets. Alongside the analysis engine, the product tracks the user's real and paper portfolios, marks them to market, and shows performance against a market benchmark (S&P 500 for US; Nifty 50 / BSE 100 for India). The analysis is powered by a multi-agent orchestration (Google ADK) whose specialist agents call data sources exposed as MCP servers.

## 2. Goals

- Give retail investors a personal, portfolio-aware equity-research analyst that produces **cited, auditable** recommendations rather than opaque signals.
- Score every buy/sell/trim idea **relative to the user's existing holdings** — concentration, sector overlap, correlation, and risk budget — so recommendations reflect the real rebalancing decision.
- Cover both **US and Indian** markets, with market-appropriate data, benchmarks, currency, and disclosures.
- **Track and display** the user's real and paper portfolios: live-ish valuation on request, historical performance, and comparison against the relevant market benchmark.
- Maintain an **auditable track record** of the product's own recommendations scored against actual forward returns (which doubles as the evaluation harness).
- Be **production-grade**: evaluated, observable, cost-controlled, guardrailed, GCP-native now and cloud-agnostic in architecture.
- **Validate cheaply first**: prefer free / open-source models, data, and tooling in v1; upgrade to paid providers only after the concept is proven.
- Be **architected for internet scale** — able to grow to millions of users if the product succeeds — without over-building v1.

## 3. Non-Goals

- **No real trade execution.** The product never places orders, never connects to a broker for write/trade actions, and never moves real money. Real holdings are tracked read-only for display only.
- Not a registered investment adviser (RIA) service and not personalized financial advice; no fiduciary or advisory relationship is created.
- Not a full trading platform, order-management system, or brokerage.
- Not a tax-filing, accounting, or portfolio-accounting system of record.
- v1 user scope is individual retail users (not a full enterprise multi-tenant rollout on day one) — but the architecture must **not preclude internet scale (millions of users)**; see NFR Scalability.
- Not options/derivatives/crypto analysis in v1 (equities and equity ETFs only).

## 4. Personas / Actors

- **US retail investor** — holds US-listed equities/ETFs; benchmarks against S&P 500; wants new ideas and verdicts on current holdings.
- **India retail investor** — holds NSE/BSE-listed equities/ETFs; benchmarks against Nifty 50 / BSE 100; same needs, India-specific data and disclosures.
- **The product's runtime agents** — first-class consumers of the MCP tool layer (analysis agents that call data tools), distinct from human users.
- **Operator / admin** (internal) — configures data sources, monitors cost and health, manages evaluation and guardrails.

## 5. Key Use Cases (summary)

1. **Onboard & profile** — user sets market, interests, risk profile, and imports holdings.
2. **Evaluate a holding** — "Should I trim / add / hold / sell TICKER given my portfolio?" → cited verdict.
3. **Discover new ideas** — "Find new stocks that fit my portfolio and risk profile" → ranked, cited candidates.
4. **Rebalance view** — buy and sell candidates ranked on one rubric against each other.
5. **Track performance** — view real and paper portfolio value and return vs benchmark over time.
6. **Paper trade** — act on an idea in a simulated portfolio and watch it play out.
7. **Review track record** — see how the product's past recommendations performed against forward returns.

---

## 6. Functional Requirements

Priorities: **P0** = Must Have, **P1** = Should Have, **P2** = Could Have. IDs are stable references.

### 6.1 Profile & Onboarding

- [ ] **F1 (P0)** Capture user profile: target market (US or India), sector/theme interests, risk profile (conservative → aggressive), and stated intent (discover new ideas vs evaluate existing holdings).
- [ ] **F2 (P0)** Risk profile drives downstream behavior (position-sizing guidance, volatility tolerance, portfolio-fit scoring thresholds).
- [ ] **F3 (P1)** Allow multiple portfolios per user (e.g., a real portfolio and one or more paper portfolios), each tagged by market.
- [ ] **F4 (P2)** Profile editable over time; changes are versioned so past recommendations remain interpretable against the profile in effect at the time.

### 6.2 Portfolio Ingestion & Tracking (read-only)

- [ ] **F5 (P0)** Import real holdings via **manual entry** and **CSV upload** (ticker, quantity, cost basis, currency, market).
- [ ] **F6 (P0)** Store holdings with quantity, cost basis, and acquisition date; support multiple positions and cash balance.
- [ ] **F7 (P0)** **Read-only** at all times for real holdings — the system never places or modifies real orders (enforces Non-Goal §3).
- [ ] **F8 (P1)** Optional **read-only broker/aggregator connection** to sync real holdings (e.g., India read APIs; US aggregator/broker read APIs). Read-only scopes only.
- [ ] **F9 (P2)** Corporate-action awareness (splits, dividends) applied to holdings and cost basis.

### 6.3 Valuation & Performance vs Benchmark

- [ ] **F10 (P0)** Mark holdings to market: compute current value on demand and on a scheduled cadence; store valuation snapshots for history.
- [ ] **F11 (P0)** Display current portfolio value, per-position value, unrealized gain/loss, and cash — for both real and paper portfolios.
- [ ] **F12 (P0)** Compare portfolio performance against the market benchmark: **S&P 500** (US), **Nifty 50** and/or **BSE 100** (India), over matching periods.
- [ ] **F13 (P0)** Compute returns correctly under cash flows: **time-weighted return (TWR)** for fair benchmark comparison and **money-weighted return (MWR/IRR)** for the user's personal return. Method shown and labeled clearly.
- [ ] **F14 (P0)** Benchmark comparison available for **both real and paper** portfolios.
- [ ] **F15 (P1)** Configurable comparison windows (1M, 3M, YTD, 1Y, since-inception) and multiple benchmarks per market.
- [ ] **F16 (P2)** Risk-adjusted metrics (volatility, max drawdown, Sharpe) for portfolio vs benchmark.

### 6.4 Analysis Engine (multi-agent)

- [ ] **F17 (P0)** For an existing holding, produce a verdict — **trim / add / hold / sell** — with rationale.
- [ ] **F18 (P0)** For discovery, produce a **ranked set of new candidate stocks** that fit the user's profile and portfolio gaps.
- [ ] **F19 (P0)** Score every candidate (buy and sell) on a **common rubric** and rank buy vs sell ideas against each other (rebalancing view).
- [ ] **F20 (P0)** **Portfolio-fit scoring** (the differentiator): each idea scored relative to current holdings — concentration, sector overlap, correlation, and risk-budget impact.
- [ ] **F21 (P0)** Analysis composed of specialist agents: **fundamental, technical, sentiment & filings, risk, portfolio-fit, report-writer**, coordinated by an **orchestrator**.
- [ ] **F22 (P0)** Deterministic steps (data fetch, ratio/return computation, logging) implemented as plain services, not agents; agents used only where judgment is required.
- [ ] **F23 (P1)** Devil's-advocate / bear-case pass on any bullish recommendation (risk agent).
- [ ] **F24 (P1)** Configurable analysis depth (quick vs deep) to control latency and cost per request.

### 6.5 Research Notes (cited & auditable)

- [ ] **F25 (P0)** Every recommendation is delivered as a **research note** with a rating and a concise rationale.
- [ ] **F26 (P0)** **Every material claim is cited** to a source (a filing, a data point, a news item) — citations are first-class, not decorative.
- [ ] **F27 (P0)** Each note carries the mandatory **not-financial-advice / do-your-own-diligence** disclaimer and a timestamp + data-as-of marker.
- [ ] **F28 (P1)** Notes are exportable (PDF/markdown) and stored for later review.

### 6.6 Recommendation Tracking / Track Record / Evaluation

- [ ] **F29 (P0)** Log every issued recommendation with timestamp, price at issue, market, and rationale reference.
- [ ] **F30 (P0)** Score recommendations against **actual forward returns** over defined horizons (e.g., 7/30/90 days) to build an auditable track record.
- [ ] **F31 (P0)** The recommendation-tracking data set is the **evaluation harness** for the analysis engine (offline eval and regression).
- [ ] **F32 (P1)** Display the track record to the user (e.g., hit rate vs benchmark) with honest, non-misleading framing.

### 6.7 Paper Trading (simulated only)

- [ ] **F33 (P0)** A simulated portfolio the user can act on: ideas execute as **virtual** buys/sells; positions, cash, and P&L update as if real.
- [ ] **F34 (P0)** **US** paper fills via a paper-trading broker sandbox (e.g., Alpaca); **India** via internal fill simulation on live/EOD prices.
- [ ] **F35 (P0)** Paper trading is clearly labeled as simulated everywhere; **no path to real-money execution** exists in the product.
- [ ] **F36 (P1)** Human-in-the-loop confirmation before any simulated action taken on the user's behalf.

### 6.8 Market Coverage & Data Freshness

- [ ] **F37 (P0)** Support **US** and **India** equities and equity ETFs, with market-appropriate tickers, currency, trading calendar, and disclosures.
- [ ] **F38 (P0)** Provide **near-real-time data on request**; a caching layer prevents redundant provider calls and controls cost/latency.
- [ ] **F39 (P1)** Clear **data-as-of** indicators wherever a value or quote is shown (never imply freshness the data doesn't have).

### 6.9 MCP Tool Layer

- [ ] **F40 (P0)** Data sources exposed to agents as **MCP servers**: market data, filings, news/sentiment, and paper-trading. Focused per-domain servers, not a monolith.
- [ ] **F41 (P0)** API keys and provider credentials live **inside the MCP servers**, never exposed to the agent/LLM layer.
- [ ] **F42 (P0)** Each MCP server enforces caching, rate limiting, and clean semantic error mapping.
- [ ] **F43 (P1)** MCP servers runnable as local processes in dev and as independently deployable services in prod.
- [ ] **F44 (P2)** At least one custom-built MCP server (e.g., filings normalization across US + India) as a reusable artifact.

### 6.10 Dashboard / UI

- [ ] **F45 (P0)** Web dashboard: watchlist + holdings, ranked buy/sell ideas, portfolio value and benchmark comparison, drill-down into cited research notes.
- [ ] **F46 (P0)** Every AI-generated output visibly attributes the analysis and shows the disclaimer.
- [ ] **F47 (P1)** Real vs paper portfolios shown side by side with benchmark overlays.
- [ ] **F48 (P2)** Alerts/notifications when a holding's thesis materially changes or a new high-fit idea appears.
- [ ] **F53 (P1)** **Progressive Web App (PWA)** — installable, responsive, add-to-home-screen, offline-tolerant shell (cached last-known holdings/valuation views), and push-capable for alerts (F48). No-flash first paint for theme/state (per engineering-protocol §5.28).

### 6.11 Guardrails & Compliance Controls

- [ ] **F49 (P0)** Mandatory disclaimer surfaced on every recommendation and report (not advice; DYODD; display-only).
- [ ] **F50 (P0)** Guardrails against prompt-injection via ingested content (filings/news may contain adversarial text); untrusted tool output is treated as data, not instructions.
- [ ] **F51 (P0)** No output that could be construed as a personalized guarantee, promise of return, or instruction to transact with real money.
- [ ] **F52 (P1)** Configurable content/response guardrails and refusal behavior for out-of-scope asks.

### 6.12 Architecture: Modularity & Cloud-Agnostic (pluggability)

Cloud-agnostic is not only a deployment target — it is an implementation discipline. The system is built from replaceable modules so any part can be swapped without rewriting the rest.

- [ ] **F54 (P0)** **Modular by construction** — each capability (orchestrator, each analysis agent, each MCP server, valuation, benchmark, portfolio store, UI) is an independently replaceable module behind a stable, documented interface. Any module can be plugged in or out without changing others.
- [ ] **F55 (P0)** **No cloud SDK in core logic** — domain, agent, and MCP code never import a cloud-specific SDK directly. Cloud services (LLM, data store, queue, blob storage, hosting) sit behind provider-agnostic interfaces/adapters, so switching a provider is an adapter change, not a core rewrite.
- [ ] **F56 (P1)** **Portability proven by design** — at least the LLM provider and the primary data/object store have a documented alternative-adapter path (even if only one adapter is implemented in v1), so the cloud-agnostic claim is demonstrable, not aspirational.
- [ ] **F57 (P1)** **Pluggable data/model sources** — market-data, filings, news, and model providers are configuration-selectable, enabling the open-source/free-first → paid upgrade path (Goals) with no code change to consumers.

---

## 7. Data Sources (per market)

| Domain | US | India | Build vs Buy |
|---|---|---|---|
| Market data (quotes, history, fundamentals) | Polygon / FMP / Alpha Vantage | NSE/BSE-capable provider (e.g., a licensed data vendor) | Build thin server over provider |
| Benchmarks | S&P 500 | Nifty 50 / BSE 100 | Via market-data server |
| Filings | SEC EDGAR (10-K/10-Q/8-K) | BSE/NSE announcements, SEBI filings | Build (normalize both) |
| News / sentiment | News API + analyst ratings; optional X via Grok | India financial news; optional X via Grok | Mix |
| Paper trading | Alpaca paper sandbox | Internal fill simulation | Buy (US) / Build (India) |
| Portfolio & user state | Internal store | Internal store | Internal |

> Provider selection is a design-phase decision (licensing, cost, India coverage quality). Requirements here are provider-agnostic. **v1 prefers free / open-source tiers** (e.g., yfinance, Alpha Vantage free tier, SEC EDGAR, NSE/BSE public data, open-source or free-tier models); paid providers are introduced later behind the same adapters (F57).

## 8. Analytics, Logging & Evaluation Requirements

- Per-recommendation logging (timestamp, price-at-issue, market, horizon) for track-record scoring (F29–F31).
- Forward-return scoring jobs at defined horizons; results stored for eval and user-facing track record.
- Agent/LLM tracing: per-request tool calls, tokens, latency, and cost, without leaking user PII into logs.
- Data-freshness and cache-hit metrics per MCP server.
- Offline evaluation sets for regression testing of the analysis engine (non-determinism-aware; see §10).

**Open decision:** granularity/retention of per-request logs vs aggregated metrics, and user-data retention windows per market.

## 9. Non-Functional Requirements

| Category | Requirement | Priority |
|---|---|---|
| Performance | Interactive analysis returns within a few seconds for quick mode; deep mode may take longer but streams progress. Valuation refresh on request is prompt. | P0 |
| Scalability | Architected for **internet scale — up to millions of users** if successful. Stateless services, horizontal scaling per component, MCP servers and app scale independently, data model and valuation jobs designed for high cardinality. Not over-built for v1, but nothing in the design precludes that scale. | P0 |
| Security & Privacy | Provider keys isolated in MCP servers; strict per-user data isolation; no user sees another's portfolio or activity. Compliant with applicable data-protection law (incl. India DPDP Act). | P0 |
| Deployment | **GCP-native now** (Vertex AI/Gemini, Cloud Run, BigQuery, Firestore). Architecture **cloud-agnostic** and **modular/pluggable** (§6.12): cloud services behind interfaces; agent/MCP layer portable; modules swappable without core rewrites. | P0 |
| Cost control | Per-request LLM and data cost bounded; caching mandatory; runtime token budget tracked (see §10). | P0 |
| Reliability of AI output | Recommendations reproducible enough to evaluate; guardrails prevent unsafe/ungrounded claims; citations required. | P0 |
| High Availability | No single point of failure on the core read/valuation path. | P1 |
| Observability | Metrics, logs, and traces for operators without leaking sensitive content. | P0 |
| Usability | Clear disclaimers, clear data-as-of markers, simple onboarding, honest track-record framing. | P0 |
| Compliance | Display-only positioning maintained end to end; no feature introduces trade execution or advisory relationship. | P0 |

## 10. AI / Agent-Specific Requirements

- [ ] **A1 (P0)** **Non-determinism handling** — the analysis engine is validated with evaluation sets and acceptance criteria, not one-off unit tests; "passed once" is never treated as reliable.
- [ ] **A2 (P0)** **Prompt-injection defense** — content fetched from filings/news/web is untrusted; agents never execute instructions embedded in tool output (cross-ref F50).
- [ ] **A3 (P0)** **Runtime token/cost discipline** — per-request budgets, caching, and model-tier selection; cost tracked as a first-class metric (distinct from build-time token discipline in the engineering protocol).
- [ ] **A4 (P0)** **Human-in-the-loop** before any action taken on the user's behalf (paper trades); the user is always the decision-maker.
- [ ] **A5 (P1)** **Model attribution** — outputs record which model/agent produced them (supports evaluation and the multi-model protocol).
- [ ] **A6 (P1)** **Groundedness checks** — recommendations must trace to retrieved evidence; ungrounded claims are flagged or withheld.

## 11. Compliance & Legal Positioning

- The product is **informational and display-only**; it is **not investment advice** and creates no advisory/fiduciary relationship (US: not an RIA service; India: not a SEBI-registered investment adviser service).
- **No real-money execution** anywhere in the product; real holdings are tracked read-only for display.
- Mandatory disclaimers on every recommendation, report, and performance view.
- Data-protection compliance for user data in both jurisdictions (including India's DPDP Act); read-only broker connections use least-privilege, read-only scopes.
- Market-data and news redistribution respects provider licensing terms (design-phase check per provider).

## 12. Constraints & Assumptions

- Users accept manual/CSV import for holdings initially; broker read-sync is a later enhancement.
- Near-real-time data implies paid data providers; a caching layer is mandatory, not optional.
- India true broker paper-trading APIs are thin; India paper trading is simulated internally.
- Consumer AI subscriptions do not provide API access; separate API accounts/billing are required for Gemini/Grok/etc.
- GCP is the initial platform; no cloud-specific SDK is imported directly by the agent/MCP layer, to preserve portability.
- Equities and equity ETFs only in v1 (no options/derivatives/crypto).
- **Open-source / free-first.** v1 favors free or open-source models, data, and tooling to validate cheaply; premium data and higher-tier models are introduced only after the concept is proven. Because sources are pluggable (F57), this upgrade is a configuration/adapter change, not a rewrite.
- Internet-scale (millions of users) is a design constraint on the architecture, not a v1 launch target — v1 is not over-built, but no decision may foreclose that scale.

## 13. Open Questions / Decisions to Resolve in Design

1. Which specific market-data provider(s) give the best India coverage at acceptable cost and licensing?
2. TWR and MWR both shown, or one primary with the other on demand? Default benchmark for India — Nifty 50 or BSE 100?
3. Per-request log granularity and per-market data-retention windows.
4. Framework confirmation: ADK as primary vs a LangGraph prototype comparison before committing (per earlier discussion).
5. Where Grok's X access fits at runtime (sentiment source) vs dev-time only.
6. Real-holdings sync: which read-only broker/aggregator integrations, and in which phase.

---

## 14. Traceability & Next Documents

Each functional requirement (F#) and AI requirement (A#) will be traced to an implementation phase/PR in the project backlog (`docs/backlog.md`) per the Multi-Agent Engineering Protocol v4.0 (§7.7). Next documents: **Architecture & Design** (agent designs, MCP server specs, data model, cloud-agnostic boundaries, sequence diagrams) and **Implementation Phases** (multi-week roadmap to production).

*Structure adapted from the enterprise-llm-gateway requirements document and enhanced for Portfolio Copilot.*
