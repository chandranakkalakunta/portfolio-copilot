# Agent Framework Spike — ADK vs LangGraph (comparison)

**Phase:** 1 (1.2 ADK, 1.3 LangGraph, 1.4 decision)
**Date:** 12 August 2026
**Author:** Strategist (synthesized from the live spike; §7.6)
**Outcome:** ADK selected as primary; LangGraph retained as the portability-proof alternate adapter. See ADR-0012.

## What was built

The identical slice was implemented twice behind `AgentFrameworkPort`: an agent with a fixed instruction and a single stub tool (`get_quote`), calling **Vertex Gemini `gemini-2.5-flash` @ us-central1 (keyless ADC)**, returning a typed `AnalysisResult`. Parity was held (same instruction, tool, model, region). Both produced correct, equivalent output:

- ADK → `"The current price of AAPL stock is 232.1 USD."`, `tool_calls=["get_quote"]`
- LangGraph → `"The current price of AAPL is 232.10 USD."`, `tool_calls=["get_quote"]`

## Head-to-head (observed facts + assessment)

| Criterion (§16) | ADK | LangGraph | Edge |
|---|---|---|---|
| Adapter LOC (engine.py) | 89 | 112 | ADK |
| Agent API | `google.adk.agents.Agent` + `InMemoryRunner` | `create_react_agent` → `CompiledStateGraph.ainvoke` | Even |
| LLM wiring (Vertex) | model string + env (`GOOGLE_GENAI_USE_VERTEXAI`, project, location) | `ChatVertexAI(model, project, location)` | ADK (fewer moving parts) |
| Tool binding | plain callable in `tools=[…]` | `@tool` LangChain wrapper | ADK (simpler) |
| Vertex/Gemini nativeness | first-class (Google) | via `langchain-google-vertexai` (flagged **deprecated** → `langchain-google-genai`) | **ADK** |
| Multi-agent / control | native sub-agents + workflow agents (sequential/parallel) | explicit `StateGraph`, checkpointing, interrupts | **LangGraph** (more control) |
| State / checkpointing | session services | first-class checkpointer + human-in-loop interrupts | **LangGraph** |
| Streaming / tracing | ADK event stream | graph streaming; LangSmith present transitively | Even |
| Dependency weight | single `google-adk` (+ genai) | larger tree (langgraph + langchain-core + vertexai stack + LangSmith) | **ADK** |
| Ecosystem / community | newer, Google-centric | larger, more examples | LangGraph |
| Ecosystem churn (observed) | ADK experimental warnings | two deprecation notices in one slice (`ChatVertexAI`, `create_react_agent`) | **ADK** (less churn exposure) |
| Testability (hermetic) | monkeypatch runner | patch LLM + graph | Even |
| Portability past the port | clean (behind `AgentFrameworkPort`) | clean | Even |

## Analysis

Both frameworks did the job cleanly, and the port abstraction held — neither leaked past `AgentFrameworkPort`, so the choice is reversible. The decision therefore turns on fit to *this* project rather than raw capability:

- **GCP nativeness** is a first-order factor here (ADR-0002, Vertex/Gemini keyless). ADK is Google-native and lighter; LangGraph reached Vertex through an integration the LangChain ecosystem has already flagged as deprecated — a live signal of the ecosystem churn that is a known maintenance tax.
- **Simplicity / dependency weight** favor ADK (fewer lines, one primary dependency, plain-callable tools), which matters for CI weight and long-term maintenance.
- **LangGraph's genuine advantage** is more mature control-flow primitives — explicit `StateGraph`, checkpointing, and human-in-the-loop interrupts — which are attractive for our orchestrator + specialists + **runtime reviewer gate** (ADR-0006). This is the one area where LangGraph is meaningfully ahead, and it is why we do **not** discard it.

## Decision

**ADK is the primary framework.** LangGraph's adapter is retained as the portability proof (F56) and the fallback if ADK's youth or control-flow limits bite as orchestration grows (especially the reviewer-gate and multi-agent loops). Because everything sits behind `AgentFrameworkPort`, switching primary later is an adapter change, not a core rewrite.

## Follow-ups

- Address the ADK experimental function-declaration warning as the tool surface stabilizes.
- If LangGraph is ever promoted, migrate its LLM path off the deprecated `ChatVertexAI` to `langchain-google-genai`, and `create_react_agent` to the current agent constructor.
- Revisit if ADK proves limiting for complex control flow (checkpointing / interrupts) — LangGraph adapter already exists to switch to.
