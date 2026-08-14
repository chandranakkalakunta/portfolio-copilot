# Portfolio Copilot — UI/UX Specification

**Document:** UI/UX Spec (living) · **Version:** 0.1 · **Status:** Active
**Owner:** Strategist (design lead) · **Location on merge:** `docs/design/ui-spec.md`
**Reference mockup:** `docs/design/ui-mockups/portfolio-overview.png`

> Living document. **v0 (now)** fixes the design language, information architecture, tokens, and invariants so every phase's UI increment is consistent. It **deepens toward Phase 6** (full dashboard, PWA, WCAG 2.1 AA, framework choice) with per-screen wireframes once the data those screens show exists. It does not pre-spec visuals for features not yet built.

---

## 0. Failure modes this spec exists to prevent

Carried from prior experience; each maps to an enforced mechanism. If a proposal violates one, it's wrong regardless of how it looks.

| Failure mode | Mechanism that prevents it |
|---|---|
| Boxes too big; space out of proportion | Fixed **spacing scale** (§3) + **layout caps** (§4). No hardcoded px outside tokens; components have defined padding/size — they don't grow to fill. |
| Pages not linked properly | **Information architecture** (§5): one app shell, a **route table** with explicit entry/exit links, and no dead-ends (every screen has empty/error states in §6). |
| Fixed repeatedly, still broke | **Single source of truth** (tokens in §3, consumed everywhere), **component/state matrix** (§6, states specified once and reused), CSS discipline (§7), and the **§8.2 rule**: a UI bug that survives one fix triggers root-cause diagnosis, not another patch. |

---

## 1. Design principles

- **Calm, precise, trustworthy.** This is a display-only, cited, as-of financial instrument. Legibility and hierarchy over decoration.
- **Provenance is the product.** As-of time + source on **every** value is the signature, not an afterthought.
- **Spend boldness in one place.** The provenance/data treatment is the one memorable element; everything else stays quiet.
- **Accessible by construction.** Gain/loss never relies on color alone; keyboard focus visible; reduced motion respected. (WCAG 2.1 AA is a Phase 6 gate — we build toward it from v0, not retrofit.)

## 2. Design language (approved "Ledger" direction)

Sans for interface, **monospace for all data** (figures, tickers, timestamps, citations), tabular numerals throughout. Cool near-white surfaces, hairline rules only where real tabular data lives, one accent. See the reference mockup for the canonical look.

## 3. Design tokens — the single source of truth

Defined once (CSS custom properties); **every** color/space/size in the app references a token. No literals in component styles.

**Color**

| Token | Value | Use |
|---|---|---|
| `--paper` | `#fbfbfc` | page background |
| `--card` | `#ffffff` | surfaces |
| `--ink` | `#14161a` | primary text |
| `--muted` | `#6b7280` | secondary text |
| `--faint` | `#9aa0a8` | tertiary / stamps |
| `--line` | `#ebecef` | hairline borders |
| `--green` (accent) | `#16513b` | brand, primary actions, portfolio series — **the only brand-tied token; swap to re-skin** |
| `--gain` | `#157a4e` | positive values |
| `--loss` | `#b03a2e` | negative values |

**Type** — `--sans` (UI) / `--mono` (data). Scale: `32 / 20 / 15 / 13 / 11`px. Money and tabular data always `--mono` + `tabular-nums`.

**Spacing** — 8pt scale, tokens only: `4 · 8 · 12 · 16 · 20 · 24 · 32 · 48`. Card padding: 16px (compact) / 20px (comfortable). **No other gap/padding values are permitted.**

**Radius / border / elevation** — radius `12px` cards, `16px` outer shell, `999px` pills. Borders `1px var(--line)`. Elevation: one soft resting shadow for the app surface; cards are flat with borders (no stacked shadows).

## 4. Layout system

- **Content max-width 880px** for reading/overview screens; card grids collapse to single column below **620px**. (Wide dashboard layouts are a Phase 6 extension, specified then.)
- **Cards do not grow to fill** — they size to content within the grid; a single card never exceeds the content column.
- **Density is defined, not emergent:** stat rows use the compact padding; panels use comfortable. Vertical rhythm follows the spacing scale.

## 5. Information architecture

**App shell (persistent):** provenance bar (display-only · not advice · as-of · source) → top bar (wordmark + primary nav + user menu). Present on every authenticated screen; defined once.

**Screen map & route table** — every screen, its job, and how you reach/leave it (no orphans):

| Route | Screen | Job | Reached from | Leads to |
|---|---|---|---|---|
| `/` (signed out) | Sign in | Google Sign-In + disclaimer | app entry | → Overview (on auth) |
| `/` (signed in) | **Portfolio overview** | value, P&L, holdings, TWR vs benchmark | nav "Overview" | → Holding detail, Analyze |
| `/holdings/:id` | Holding detail | add/edit a holding; per-holding figures | Overview row | → Overview, Analyze(ticker) |
| `/analyze` | Analysis | cited note for a ticker | nav "Analyze", holding | → Recommendations (on log) |
| `/recommendations` | Recommendations log | issued recs + price-at-issue | nav "Recommendations" | → Analyze, Holding |
| `/profile` | Profile & settings | base market, currency, sign out | user menu | → Sign in (on sign-out) |

*Phase 5+ adds Discover / Rebalance; Phase 6 adds the full dashboard + notifications + settings depth. Added to this table when built.*

**Navigation states:** active item marked; back returns to the referring screen; every screen is deep-linkable by route.

## 6. Component inventory & state matrix

Each component is defined once with **all** states; screens compose these — they do not re-implement them. Every component must specify loading / empty / error / populated (dead-ends are the bug).

| Component | Loading | Empty | Error | Populated |
|---|---|---|---|---|
| **StatCard** (value + delta) | skeleton bar | `—` with label | dash + inline "retry" | value (mono) + signed delta w/ arrow+color |
| **HoldingsTable** | 3 skeleton rows | "Add your first holding" CTA (never blank) | row-level error + retry | rows: ticker, qty·cost, price, value, P&L |
| **PerformancePanel** (TWR/benchmark) | skeleton chart | "Needs ≥ N snapshots — check back after the next valuation" | message + retry | TWR, benchmark, growth chart, MWR-on-demand |
| **CitedNote** | "Analyzing…" progress | prompt to pick a ticker | failure reason + retry (not a blank) | note body + citation table (source · as-of) |
| **ProvenanceStamp** | — | — | shows "data unavailable" | as-of + source; **stale** (older than threshold) shows a subtle warning |
| **MoneyValue** (primitive) | — | `—` | — | mono, tabular, currency-formatted, signed for deltas |

## 7. Display-only invariants (every screen inherits)

- **As-of + source on every value** (F45/F46) — via `ProvenanceStamp` / `MoneyValue`; no naked number.
- **Gain/loss = sign + arrow + color together** — never color alone (accessibility).
- **Disclaimer present** — "not investment advice · display-only · never executes trades."
- **Currency & locale formatting** (O28) — one formatter; US/USD now, India/INR in Phase 8; no ad-hoc number strings.

## 8. Implementation discipline (prevents the "fixed but still broke" class)

- **Tokens only** — no literal colors/spacing in component CSS; change once, everywhere.
- **Component-scoped class names**, single stylesheet source; avoid type-selector vs element-selector specificity collisions (a known cause of styles canceling out).
- **State drives render** — UI is a function of state; no imperative DOM patching that drifts from state. (This is a strong input to the **Phase 6 framework choice** — predictable state-to-DOM prevents whole classes of whack-a-mole bugs.)
- **§8.2 rule:** a UI bug that survives one fix → stop and run a read-only diagnosis (specificity? duplicated state? stale build/cache?) → fix the cause. No second guess-patch.
- **Quality floor, unannounced:** responsive to mobile, visible keyboard focus, reduced-motion honored.

## 9. Per-phase UI increments (so increments never fight)

| Phase | UI added |
|---|---|
| 3 | Portfolio overview (value, P&L, holdings), Performance vs S&P 500 panel, Recommendations log — all in this system |
| 4 | Full cited analysis surface (multi-agent), reviewer/guardrail affordances |
| 5 | Discovery (ranked ideas), rebalance view |
| 6 | **Full dashboard**, installable PWA, notifications, settings depth, WCAG 2.1 AA sign-off, **framework choice** |
| 7 | Paper-trading + track-record surfaces |
| 8 | India market: INR formatting, Nifty benchmark |

## 10. Open / deferred to Phase 6

- Web framework selection (state model per §8 is the key criterion).
- Per-screen wireframes and motion spec (prototyped interactively when the data exists).
- Dark mode (token set is structured to support it later).
- Full brand system if Chandra AI Labs formalizes one (drops into `--green` + wordmark).
