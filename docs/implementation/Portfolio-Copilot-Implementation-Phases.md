# Portfolio Copilot — Implementation Phases

**Document:** Implementation Phases (Roadmap)
**Version:** 0.2 (draft)
**Last updated:** 14 August 2026
**Status:** Active (living roadmap)
**Related documents:** `docs/requirements/Portfolio-Copilot-Requirements.md` (v0.4), `docs/architecture/Portfolio-Copilot-Architecture.md` (v0.1), `docs/adr/` (0001–0015), `docs/backlog.md`, `docs/phase-closure/`, `docs/learnings/`, Multi-Agent Engineering Protocol v4.3 (`chandra-prompts/`).

> **Positioning & disclaimer.** Portfolio Copilot is **display-only** — no real trades, no money movement. All outputs are informational and **not investment advice**. This holds in every phase.

---

## 1. How to read this roadmap

This roadmap turns the requirements (F#/A#/O#) and ADRs into an ordered, PR-gated build. It follows two disciplines:

1. **Engineering protocol phase-gating** (v4.3 §2–§3). Each phase is broken into sub-phases; **one sub-phase per Worker prompt (Claude Code or Grok CLI)**; design discussion precedes code; the Coordinator validates in a fresh terminal and merges per risk tier; risk-sensitive work gets cross-model review (Grok). Nothing lands on `main` except through a PR.
2. **Walking skeleton, then breadth.** We build a thin *end-to-end* slice early (auth → a holding → one agent → a cited note in the UI, deployed), then widen it. This de-risks integration and gives a working product to iterate on, rather than a big-bang integration at the end.

Each phase below lists its **goal**, **key requirements/ADRs**, **deliverables**, and **exit criteria**. Sub-phase breakdown and execution prompts are produced per-phase at build time (not pre-written), per protocol §2.1.

**Roles at build time:** Strategist (Claude) designs prompts and reviews; Coordinator (Chandra) runs prompts and merges; Worker (Claude Code / Grok) implements on feature branches; Reviewer (the other model) does adversarial review on risk-sensitive PRs.

## 2. Milestones

- **M1 — Foundations & Walking Skeleton** (Phases 0–2): rails in place; one thin vertical slice deployed to staging.
- **M2 — MVP (US, single market)** (Phases 3–6): valuation + benchmark, full analysis engine, dashboard/PWA, auth, notifications — usable for US equities.
- **M3 — Beta** (Phases 7–8): paper trading + track record; India market coverage.
- **M4 — Production Hardening & GA** (Phases 9–10): DR, SLOs, governance, scale readiness.

---

## 3. Phases

### Phase 0 — Foundations & Rails
**Status:** Complete — see `docs/phase-closure/phase-0.md`.
**Goal:** the production-grade skeleton before any feature — repo, CI/CD, environments, keyless identity, hexagonal scaffolding, observability baseline.
**Requirements/ADRs:** O1–O6 (CI/CD, environments, IaC), F55 (no cloud SDK in core), ADR-0001 (hexagonal), ADR-0002 (GCP), ADR-0009 (keyless), ADR-0011 (tech stack).
**Deliverables:** monorepo layout (architecture §18); `core/ports` interfaces stubbed; CI (lint, type-check, unit, secret/dependency scan) with branch-protected `main`; Terraform for dev/staging + keyless WIF deploy to Cloud Run; a "hello, healthcheck" service deployed; CHANGELOG, `docs/backlog.md`, ADR flow live.
**Exit criteria:** a trivial service builds in CI and deploys to staging via keyless CD; no core package imports a cloud SDK (CI-checked); rollback verified.

### Phase 1 — Agent Framework Spike (ADK vs LangGraph)
**Status:** Complete — see `docs/phase-closure/phase-1.md`.
**Goal:** decide the framework by building, not guessing.
**Requirements/ADRs:** F21, F54, architecture §16, ADR-0012 (moves Proposed → Accepted here).
**Deliverables:** the same minimal slice (one specialist agent + orchestrator calling one stub tool) implemented against **both** an ADK adapter and a LangGraph adapter of `AgentFrameworkPort`; a written comparison; **ADR-0012 accepted**.
**Exit criteria:** primary framework selected and recorded; the non-primary adapter retained as portability proof (F56); core untouched by the choice.

### Phase 2 — Walking Skeleton (thin vertical slice)
**Status:** Complete — see `docs/phase-closure/phase-2.md`.
**Goal:** one working end-to-end path, deployed.
**Requirements/ADRs:** F58 (Google Sign-In), F5/F6 (manual holding), F40–F42 (market-data MCP), F17/F25–F27 (one agent → cited note), F45 (minimal UI), ADR-0003 (display-only), ADR-0005 (MCP), ADR-0015 (MCP over HTTP; supersedes ADR-0005 transport), ADR-0006 partial.
**Deliverables:** Google Sign-In via the auth port; create a portfolio + add one holding (manual); **market-data MCP server** (real quotes, cached); **fundamental agent + orchestrator** produce a cited note for one ticker; a minimal web page shows the note with disclaimer; deployed to staging.
**Exit criteria:** a signed-in user can add a holding and get a cited, disclaimed analysis for it in the browser, end to end, in staging.

### Phase 3 — Valuation, Performance & Recommendation Logging
**Goal:** portfolio tracking and honest performance.
**Requirements/ADRs:** F10–F14 (mark-to-market, TWR primary/MWR on demand, S&P 500 benchmark), F29 (log recommendations), O28 (currency formatting), ADR-0004 (stores), ADR-0010 (conventions).
**Deliverables:** valuation service (on-demand + scheduled snapshots to BigQuery); portfolio value + unrealized P&L UI; **TWR vs S&P 500** comparison with MWR on demand; recommendation logging with price-at-issue.
**Exit criteria:** a user sees current value and TWR-vs-benchmark for a real portfolio; every recommendation is logged.

### Phase 4 — Full Analysis Engine + Reviewer + Guardrails + Eval
**Goal:** the real multi-agent analysis, safe and evaluated.
**Requirements/ADRs:** F18–F24 (all specialists, portfolio-fit, depth), A1/A2/A6 (eval, injection defense, groundedness), F49–F52 (guardrails), ADR-0006 (reviewer agent), ADR-0007 (caching/cost), ADR-0008 (prompt-injection).
**Deliverables:** technical, sentiment&filings, risk, portfolio-fit, report-writer agents; **runtime Reviewer agent (Grok)** with propose→review→gate; guardrail/policy layer + prompt-injection defenses; **eval harness** gating agent/prompt changes; per-request cost/trace metrics.
**Exit criteria:** a holding verdict (trim/add/hold/sell) is produced by the full engine, reviewed, grounded/cited, within cost budget; eval suite runs in CI and gates changes.

### Phase 5 — Filings & News MCP + Discovery & Rebalance
**Goal:** new-idea discovery and the rebalance view.
**Requirements/ADRs:** F18–F20 (discovery, common rubric, portfolio-fit ranking), F40/F44 (filings + news MCP; custom filings server), F23 (bear case).
**Deliverables:** **Filings MCP** (SEC EDGAR normalized) and **News/Sentiment MCP**; discovery flow returning ranked new candidates; buy vs sell ranked on one rubric (rebalance view).
**Exit criteria:** a user gets ranked, cited new-stock ideas that fit their portfolio, alongside sell/trim candidates.

### Phase 6 — Dashboard, PWA, Notifications, Accessibility
**Goal:** the real product surface.
**Requirements/ADRs:** F45–F48, F53 (PWA), F63–F65 (notifications), O27 (WCAG 2.1 AA), O28 (i18n formatting), F46 (attribution + disclaimer).
**Deliverables:** full dashboard (watchlist, holdings, ranked ideas, benchmark chart, drill-down notes); installable **PWA** with offline shell; in-app/push/email notifications with preferences; accessibility pass; English UI, i18n-ready.
**Exit criteria:** WCAG 2.1 AA checks pass; PWA installable; alerts deliver per user preference; M2 (US MVP) complete.

### Phase 7 — Paper Trading & Track Record
**Goal:** act-and-watch, plus the credibility moat.
**Requirements/ADRs:** F33–F36 (paper trading, HITL), F30–F32 (forward scoring, track record), A4 (human-in-loop), ADR-0003 (still display-only).
**Deliverables:** **Paper-trading MCP** (Alpaca sandbox, US) with simulated portfolio + P&L; human-in-the-loop confirmation; **forward-return scoring jobs** (7/30/90d); user-facing track record with honest framing.
**Exit criteria:** a user runs a paper portfolio and sees an auditable track record; no real-execution path exists (verified).

### Phase 8 — India Market Coverage
**Goal:** second market.
**Requirements/ADRs:** F37 (India equities/ETFs), F12 (Nifty 50 primary), filings (BSE/NSE/SEBI), India paper simulation, O28 (INR formatting).
**Deliverables:** India market-data + benchmark (**Nifty 50**); filings normalization for BSE/NSE/SEBI; internal India paper-fill simulation; INR/date formatting and India disclosures.
**Exit criteria:** the full flow works for an India retail investor; M3 (Beta) complete.

### Phase 9 — Production Hardening
**Goal:** make the "production-grade" claim true.
**Requirements/ADRs:** O12–O26 (SLOs, DR/backup, incident/operability, governance, rate limiting), O10 (security/load testing), O21–O24 (retention, erasure/export, residency, audit log), F60 (account deletion).
**Deliverables:** SLOs + error budgets + alerting; tested backups + restore drills + documented RPO/RTO; runbooks + postmortem process; rate limits/quotas; data retention + right-to-erasure/export + audit log; load and security testing.
**Exit criteria:** backup restore drill passes; SLO dashboards + alerts live; erasure/export works; rate limiting enforced.

### Phase 10 — Scale Readiness & GA
**Goal:** confidence toward internet scale and general availability.
**Requirements/ADRs:** NFR Scalability, O14 (multi-zone), cost/FinOps dashboards, portability proof (F56).
**Deliverables:** load tests against scale targets; multi-zone deployment; cost dashboards + anomaly alerts; documented alternate-cloud adapter path exercised; GA checklist.
**Exit criteria:** meets SLOs under load-test scale; GA go/no-go review passes.

---

## 4. Cross-cutting per every sub-phase

Applied continuously, not as phases (protocol):

- Update **CHANGELOG.md** and **docs/backlog.md** per PR; write **ADRs** as real decisions arise (§7.5).
- **Tests before merge** (unit/integration + contract tests for MCP); **eval suite** for any agent/prompt change (A1).
- **Risk-tiered review** (§3.5): money-adjacent logic, auth, IAM/Terraform, LLM tool-call handling, and MCP contracts get full Strategist + cross-model (Grok) review.
- **Secret hygiene** and **keyless identity** throughout (ADR-0009); **display-only** invariant re-checked (ADR-0003).
- **Data-as-of** markers and **disclaimers** on every user-facing value/output.
- Per protocol **§7.9**, each phase closes with a **phase-closure report**, a **README refresh**, and any new **learnings**.

## 5. Sequencing rationale (why this order)

Rails first (Phase 0) so every later slice ships on a safe, observable pipeline. The framework spike (Phase 1) resolves the one open foundational unknown before we build on it. The walking skeleton (Phase 2) proves the hardest integration — auth + MCP + agent + UI — end to end while it's cheap to change. Value features (3–6) then broaden the skeleton into a usable US MVP. Paper trading + track record (7) add the credibility moat. India (8) is deliberately after the US flow is solid, since it mostly re-uses the same abstractions behind new adapters. Hardening and scale (9–10) come once there's a real product to harden — not before, which would be over-building (requirements §13 note).

## 6. Requirements coverage map (phase → requirements)

| Phase | Primary requirements / ADRs |
|---|---|
| 0 Foundations | O1–O6, F55, ADR-0001/0002/0009/0011 |
| 1 Spike | F21, F54, ADR-0012 |
| 2 Walking skeleton | F58, F5/F6, F40–F42, F17, F25–F27, F45, ADR-0003/0005/0015 |
| 3 Valuation | F10–F14, F29, ADR-0004/0010 |
| 4 Analysis engine | F18–F24, A1/A2/A6, F49–F52, ADR-0006/0007/0008 |
| 5 Discovery | F18–F20, F40/F44, F23 |
| 6 Dashboard/PWA | F45–F48, F53, F63–F65, O27/O28 |
| 7 Paper + track record | F33–F36, F30–F32, A4 |
| 8 India | F37, F12, O28 |
| 9 Hardening | O10, O12–O26, F60 |
| 10 Scale/GA | NFR Scalability, O14, F56 |

## 7. Immediate next step

**Phases 0–2 are complete (M1 done).** Closure reports: `docs/phase-closure/phase-0.md`, `phase-1.md`, `phase-2.md`. Next is **Phase 3 — Valuation, Performance & Recommendation Logging** (F10–F14, F29). Sub-phase breakdown is produced at build time (protocol §2.1).

*Next document (optional): a per-phase design note in `docs/design/` as each phase begins.*
