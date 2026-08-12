# ADR-0012: Agent framework selection (ADK vs LangGraph)

- **Status:** Accepted (2026-08-12) — decided after the Phase 1 spike (Proposed 2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements F21, F54; architecture §7.1, §16; behind `AgentFrameworkPort` (ADR-0001); spike write-up `docs/design/framework-spike-comparison.md`

## Context

The analysis engine needs an agent/orchestration framework. The team is GCP-centric (favoring ADK's native Vertex/Gemini integration) but also wanted the learning and de-risking of comparing ADK with LangGraph before committing. The orchestrator and agents are written against `AgentFrameworkPort` (ADR-0001), so the choice is swappable and the core is unaffected either way. The spike built the identical slice against both frameworks (Phases 1.2/1.3), both calling Vertex Gemini `gemini-2.5-flash` keyless; both produced correct, equivalent output with parity held.

## Decision

**ADK is the primary agent framework; the LangGraph adapter is retained as the portability proof (F56) and fallback.**

The spike showed both frameworks work cleanly behind the port, so the decision turned on fit to this project: ADK is Google-native (first-class Vertex/Gemini), lighter (fewer lines, one primary dependency, plain-callable tools), and showed less ecosystem churn — LangGraph reached Vertex via an integration its own ecosystem already flags as deprecated. LangGraph's real edge is more mature control-flow primitives (explicit `StateGraph`, checkpointing, human-in-the-loop interrupts) relevant to the orchestrator + reviewer gate (ADR-0006), which is exactly why its adapter is **kept**, not discarded. Full analysis: `docs/design/framework-spike-comparison.md`.

## Evaluation criteria

- Developer ergonomics and iteration speed
- Multi-agent orchestration & control (sequential/parallel/routing)
- State management and checkpointing
- Streaming support
- Tracing/observability integration
- Vertex AI / Gemini nativeness
- Testability (hermetic + eval)
- Portability cost (how much leaks past the port)

## Consequences

**Positive:** an evidence-based choice plus first-hand knowledge of both frameworks; portability proven by two working adapters behind the port; ADK's GCP-native path keeps the Vertex/Gemini integration light and low-churn.

**Negative / cost:** ADK is younger (experimental warnings observed); we carry a second (LangGraph) adapter for portability, which is maintenance not currently exercised. If ADK proves limiting on complex control flow (checkpointing/interrupts), we switch primary to the retained LangGraph adapter — a change isolated to the adapter layer.

## Alternatives considered

- **Commit to ADK now, no spike.** Fastest and GCP-native, but forgoes the comparison learning the Coordinator wants and the LangGraph portability proof.
- **Center on LangGraph.** Larger community/examples and fine-grained control, but less GCP-native; still evaluated in the spike.
- **Raw Python agent loop (no framework).** Maximum control, maximum boilerplate; rejected as the default, though the port makes it a possible future adapter.
