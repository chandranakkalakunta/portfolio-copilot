# Phase 1 — Agent Framework Spike — Closure Report

**Status:** Complete · **Closed** 2026-08-12 · **Milestone** M1

## 1. Goal

Decide the agent framework by building the same thin slice twice — not by guessing — then record the decision.

## 2. Exit criteria

| Criterion | Met? | Evidence |
|---|---|---|
| Primary framework selected and recorded | Yes | ADR-0012 **Accepted** (2026-08-12); comparison write-up `docs/design/framework-spike-comparison.md` (PR #13). |
| Non-primary adapter retained (F56) | Yes | LangGraph adapter kept behind `AgentFrameworkPort`. |
| `core/` untouched by the choice | Yes | Both adapters live in `adapters/`; core only defines the port + stub tool. |

## 3. Sub-phases / PRs

| Sub-phase | PR | Merged | What landed |
|---|---|---|---|
| 1.1 foundation | [#10](https://github.com/chandranakkalakunta/portfolio-copilot/pull/10) | 2026-08-12 | `AgentFrameworkPort`, stub tool, LLM config |
| 1.2 ADK | [#11](https://github.com/chandranakkalakunta/portfolio-copilot/pull/11) | 2026-08-12 | ADK adapter + live Vertex Gemini smoke |
| 1.3 LangGraph | [#12](https://github.com/chandranakkalakunta/portfolio-copilot/pull/12) | 2026-08-12 | LangGraph adapter + live Vertex Gemini smoke (parity) |
| 1.4 decision | [#13](https://github.com/chandranakkalakunta/portfolio-copilot/pull/13) | 2026-08-12 | Spike comparison; ADR-0012 Accepted (ADK primary) |

## 4. Key decisions & ADRs

- **ADR-0012 Accepted:** ADK is the primary agent framework; LangGraph is retained as the portability proof (F56) and fallback.
- Model/region confirmed live: Vertex Gemini **`gemini-2.5-flash` @ `us-central1`** (ADC / keyless). `gemini-2.0-flash` returned 404 in this project.
- LangGraph path: `create_react_agent` + `ChatVertexAI`; same instruction / tool / model as ADK.

## 5. Requirements covered

- **F21 / F54** — framework spike by building, not guessing.
- **F56** — non-primary adapter retained (portability proof).
- Architecture §16; decision recorded in ADR-0012.

## 6. Deferrals carried forward

- Full multi-agent orchestration, reviewer gate, and eval harness are Phase 4 (ADR-0006 / A1).
- LangGraph’s stronger control-flow primitives (checkpointing, HITL interrupts) stay unused until those phases need them.

## 7. Verification

Both adapters produced equivalent live smoke output on **AAPL** against Vertex Gemini `gemini-2.5-flash`. Hermetic unit tests cover each adapter with mocks (no network in CI).

## 8. Learnings

See `docs/design/framework-spike-comparison.md` for the head-to-head. No numbered learning in `docs/learnings/` is Phase-1-specific.
