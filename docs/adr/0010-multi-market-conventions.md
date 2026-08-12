# ADR-0010: Multi-market conventions (US + India, benchmarks, TWR/MWR)

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F12, F13, F37, F39; architecture §10; open items resolved

## Context

The product covers US and Indian equities, which differ in tickers, currency, trading calendars, filings, and benchmarks. Comparing a portfolio (which has deposits/withdrawals) to an index requires a return method that is fair; naive percentage comparison misleads once cash flows exist. Two open decisions needed resolving: the India default benchmark, and how to present return vs benchmark.

## Decision

Treat **market as a first-class dimension** on profiles, portfolios, positions, and data calls (US or India), driving currency, calendar, filings source, and benchmark. **Benchmarks:** S&P 500 for US; **Nifty 50 as the India default** (BSE 100 available as a secondary/optional comparison). **Return presentation:** compute both **time-weighted return (TWR)** and **money-weighted return (MWR/IRR)**, but present **TWR as primary** (for fair, cash-flow-neutral benchmark comparison) with **MWR available on demand** (the user's actual personal return). All values carry currency and data-as-of markers (F39).

## Consequences

**Positive:** fair benchmark comparison by default; clear, market-appropriate presentation; a single dimension cleanly parameterizes market-specific behavior.

**Negative / cost:** must maintain per-market calendars, currency handling, and benchmark series; MWR/IRR computation adds complexity even when secondary.

**Follow-ups:** confirm India market-data/benchmark provider (open item); handle FX display for users comparing across markets; corporate-action handling (F9) affects return math.

## Alternatives considered

- **BSE 100 as India default.** Broader index, but Nifty 50 is the more widely tracked large-cap reference for retail investors; BSE 100 retained as secondary.
- **Show TWR and MWR equally / MWR primary.** Equal display adds cognitive load; MWR-primary invites unfair "I beat the index" comparisons distorted by deposit timing. TWR-primary with MWR-on-demand chosen as the honest default.
- **Single global market model (ignore market differences).** Incorrect for India/US divergence; rejected.
