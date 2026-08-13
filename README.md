# Portfolio Copilot

An AI equity-research analyst that knows your portfolio. Built on an agentic framework (Google ADK) and MCP, it produces cited, personalized buy / sell / trim ideas — for both existing positions and new stocks — across US and Indian markets.

> **Not investment advice.** All outputs are informational; the user is solely responsible for their own due diligence and decisions. **Display-only** — never executes real trades.

## Status

Actively building. **Phase 0 (foundations)** and **Phase 1 (framework spike)** are complete; **Phase 2 (walking skeleton)** is in progress.

- **Phase 0 — Foundations ✓** — monorepo + pinned toolchain (Python 3.12 / uv), CI (lint/type/test), keyless CI→GCP via Workload Identity Federation, Terraform-managed infra, and a verifiable `hello` service deployed to Cloud Run.
- **Phase 1 — Framework spike ✓** — same agent slice built in both ADK and LangGraph against Vertex Gemini; **ADK selected as primary**, LangGraph retained as portability proof (ADR-0012, `docs/design/framework-spike-comparison.md`).
- **Phase 2 — Walking skeleton (in progress)** — done: market-data MCP HTTP microservice (yfinance), Firestore portfolio/profile domain, backend Google/Firebase token verification, cited fundamental note, auth-protected API, **minimal UI + Google Sign-In** (vanilla HTML/JS). Remaining: slice deploy to staging.

## Tech stack

- **Language/runtime:** Python 3.12, `uv`, `ruff`, `mypy` (strict), `pytest`.
- **Backend:** FastAPI (ADR-0014).
- **Agents:** Google ADK (primary) + LangGraph (retained) behind `AgentFrameworkPort`; Vertex AI Gemini (`gemini-2.5-flash`), keyless.
- **Tools:** MCP servers as HTTP microservices (ADR-0015).
- **Data:** Firestore (state) + BigQuery (analytical, later) behind ports (ADR-0004).
- **Cloud/CI:** GCP (Cloud Run, Artifact Registry, Secret Manager) now, cloud-agnostic via ports-and-adapters (ADR-0001); Terraform; keyless WIF deploys.

## Repository layout

```
core/          # domain + ports (NO cloud SDK imports)
  ports/       #   AgentFramework, LLM, repositories, auth interfaces
  portfolio/   #   Profile, Portfolio, Position models
  analysis/    #   spike stub tools
  config.py    #   settings (LLM, MCP, ...)
adapters/      # provider/cloud implementations of the ports
  agent_adk/   #   ADK adapter (primary)
  agent_langgraph/  # LangGraph adapter (portability proof)
  firestore/  memory/         # repository adapters
  firebase_auth/  fake_auth/  # auth adapters
mcp_servers/   # MCP HTTP microservices
  market_data/ #   yfinance: get_quote / get_fundamentals, /health
api/           # FastAPI app ( /health, /me, /config, domain routes; serves web/ at / )
web/           # Vanilla HTML/JS UI (Firebase Auth Google Sign-In; framework = Phase 6)
infra/         # Terraform (WIF, Artifact Registry, service accounts, IAM, APIs, Firestore)
scripts/       # live-smoke scripts
tests/         # hermetic tests
docs/          # product, requirements, architecture, implementation, design, adr, runbooks
.github/workflows/  # ci.yml (lint/type/test/coverage/scan) + deploy-dev.yml (keyless), gcp-auth-check.yml
docker-compose.yml  # local services (market-data MCP)
```

## Development

```
uv sync                                   # install toolchain + deps
uv run ruff check . && uv run mypy core api adapters mcp_servers tests
uv run pytest -m "not integration" --cov  # unit tests + coverage (default CI unit job)
docker compose up market-data-mcp --build # run the market-data MCP (HTTP :8081)

# Real-token UI (Google Sign-In popup). Requires Identity Platform Web client
# + authorized JavaScript origin http://localhost:8000 (console).
# Copy .env.example → .env and fill PCOPILOT_FIREBASE_*.
PCOPILOT_AUTH_BACKEND=firebase \
PCOPILOT_REPO_BACKEND=firestore \
PCOPILOT_FIREBASE_API_KEY=... \
PCOPILOT_FIREBASE_AUTH_DOMAIN=... \
PCOPILOT_FIREBASE_PROJECT_ID=... \
uv run uvicorn api.main:app --reload --port 8000
# open http://localhost:8000
```

### Integration tests

Marked `@pytest.mark.integration` (excluded from default unit runs):

1. **Firestore emulator** — install Java + Cloud SDK Firestore emulator, then:

   ```bash
   # Terminal A
   gcloud emulators firestore start --host-port=127.0.0.1:8080

   # Terminal B
   export FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
   uv run pytest -m integration -q
   ```

   If `FIRESTORE_EMULATOR_HOST` is unset, Firestore integration tests **skip** (safe without emulator).

2. **MCP HTTP** — no external network; starts an in-process HTTP server with a **fake** market-data provider (no yfinance). Included in `pytest -m integration`.

CI runs integration in a dedicated job (emulator + `pytest -m integration`).

Environment setup for a fresh GCP project is documented in `docs/runbooks/environment-setup.md` (bootstrap + `terraform apply`; only the OAuth consent screen / Web client is a manual step).

## Documentation

```
docs/
├── product/          # One-Pager (vision, positioning)
├── requirements/     # Detailed PRD (functional + non-functional + operational)
├── architecture/     # Technical architecture (C4, agents, MCP, data, deployment)
├── implementation/   # Phased build roadmap
├── design/           # Design notes (e.g., framework-spike comparison)
├── runbooks/         # Operational runbooks (environment setup, ...)
└── adr/              # Architecture Decision Records + index
```

| Document | Description |
|---|---|
| [One-Pager](docs/product/Portfolio-Copilot-One-Pager.md) | Problem, concept, agent architecture, stack, guardrails |
| [Requirements](docs/requirements/Portfolio-Copilot-Requirements.md) | Detailed PRD — goals, use cases, FRs/NFRs + operational/platform requirements (draft v0.4) |
| [Architecture](docs/architecture/Portfolio-Copilot-Architecture.md) | Technical architecture — C4, agents, MCP, data, deployment (draft v0.1) |
| [Implementation Phases](docs/implementation/Portfolio-Copilot-Implementation-Phases.md) | Phased, PR-gated build roadmap (draft v0.1) |
| [ADRs](docs/adr/README.md) | Architecture Decision Records 0001–0015 (0012 accepted: ADK primary) |
| [Design: framework spike](docs/design/framework-spike-comparison.md) | ADK vs LangGraph head-to-head and decision |

Engineering methodology: **Multi-Agent Engineering Protocol v4.1** (`chandra-prompts` repo) — Strategist / Coordinator / Worker / Reviewer, PR-gated, one sub-phase per PR.
