# ADR-0014: Backend web framework — FastAPI

- **Status:** Accepted (2026-08-12)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** ADR-0011 (tech-stack baseline, Python); architecture §4 (API/BFF), F45 (streaming); requirements F66, O31

## Context

The backend (API/BFF and service endpoints, and later agent-facing HTTP surfaces) needs a Python web framework. Requirements that bear on the choice: streaming responses for agent output (F45), typed request/response contracts that pair cleanly with our ports (ADR-0001) and MCP tool schemas, automatic API documentation, good performance toward internet scale, and no dependence on a built-in ORM (we use Firestore/BigQuery behind ports, ADR-0004).

## Decision

Use **FastAPI** (ASGI, served by uvicorn) as the standard backend web framework for all Python services. Pydantic models define typed request/response contracts; OpenAPI/Swagger is generated automatically; async endpoints support streaming (e.g., SSE) for agent output.

## Consequences

**Positive:** async-native (streaming), typed validation via Pydantic, auto OpenAPI, strong performance, large ecosystem; models double as the schema layer for tool/port contracts.

**Negative / cost:** requires discipline to avoid blocking (sync) calls inside async handlers (offload CPU/blocking work to threads/executors); an ASGI server (uvicorn) and its ops are part of the stack.

**Follow-ups:** the `/health` and `/ready` endpoints expose build ID + deploy timestamp (O31); standardize an app factory + settings pattern (pydantic-settings) as services grow.

## Alternatives considered

- **Flask.** Simple and ubiquitous, but WSGI/sync by default, no built-in validation/typing, manual OpenAPI, weaker streaming story. Rejected.
- **Django + DRF.** Batteries-included but heavyweight and ORM-centric; the ORM is unused here (ports to Firestore/BigQuery). Overkill. Rejected.
- **Litestar / Starlette.** Viable and modern (Starlette underlies FastAPI); smaller communities and less ubiquitous tooling. FastAPI chosen for ecosystem and fit.
