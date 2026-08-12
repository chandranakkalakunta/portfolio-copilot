# ADR-0012: Agent framework selection (ADK vs LangGraph)

- **Status:** Proposed — pending spike (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F21, F54; architecture §7.1, §16; behind `AgentFrameworkPort` (ADR-0001)

> This ADR is intentionally **not yet decided**. Per the engineering protocol (§7.5), a decision ADR is written when the decision is actually made — here, after a hands-on spike. It is recorded now as Proposed so the number is reserved and the decision context, options, and criteria are captured. It will move to Accepted after the spike.

## Context

The analysis engine needs an agent/orchestration framework. The team is GCP-centric (favoring ADK's native Vertex/Gemini integration) but also wants the learning and de-risking of comparing ADK with LangGraph before committing. The orchestrator and agents are written against `AgentFrameworkPort` (ADR-0001), so the choice is swappable and the core is unaffected either way.

## Decision (pending)

Build the **same minimal slice** — one specialist agent + orchestrator calling one MCP tool — against **both** an ADK adapter and a LangGraph adapter of `AgentFrameworkPort`, then select a **primary** framework and retain the other adapter as portability proof (F56). Decision to be recorded here once the spike completes.

## Evaluation criteria

- Developer ergonomics and iteration speed
- Multi-agent orchestration & control (sequential/parallel/routing)
- State management and checkpointing
- Streaming support
- Tracing/observability integration
- Vertex AI / Gemini nativeness
- Testability (hermetic + eval)
- Portability cost (how much leaks past the port)

## Consequences (anticipated)

**Positive:** an evidence-based choice plus first-hand knowledge of both frameworks; portability proven by having two working adapters.

**Negative / cost:** the spike costs time before the framework locks; two adapters to maintain until one is chosen.

## Alternatives considered

- **Commit to ADK now, no spike.** Fastest and GCP-native, but forgoes the comparison learning the Coordinator wants and the LangGraph portability proof.
- **Center on LangGraph.** Larger community/examples and fine-grained control, but less GCP-native; still evaluated in the spike.
- **Raw Python agent loop (no framework).** Maximum control, maximum boilerplate; rejected as the default, though the port makes it a possible future adapter.
