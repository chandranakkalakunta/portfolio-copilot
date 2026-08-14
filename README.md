# Portfolio Copilot

An AI equity-research analyst that knows your portfolio. Built on an agentic framework (Google ADK) and MCP, it produces cited, personalized buy / sell / trim ideas — for both existing positions and new stocks — across US and Indian markets.

> **Not investment advice.** All outputs are informational; the user is solely responsible for their own due diligence and decisions. **Display-only** — never executes real trades.

## Status

**Phase 2 (walking skeleton) is complete** and deployed to staging. Next is **Phase 3** (valuation, performance, recommendation logging).

- **Phase 0 — Foundations ✓** — monorepo + pinned toolchain (Python 3.12 / uv), CI (lint/type/test), keyless CI→GCP via Workload Identity Federation, Terraform-managed infra.
- **Phase 1 — Framework spike ✓** — same agent slice in ADK and LangGraph against Vertex Gemini; **ADK selected as primary**, LangGraph retained (ADR-0012).
- **Phase 2 — Walking skeleton ✓** — market-data MCP (HTTP), Firestore domain, Google Sign-In, cited fundamental note, auth-protected API, vanilla UI, two Cloud Run services in `pcopilot-dev`.

**Live API (dev):** https://api-552451662981.asia-south1.run.app

## Tech stack

- **Language/runtime:** Python 3.12, `uv`, `ruff`, `mypy` (strict), `pytest`.
- **Backend:** FastAPI (ADR-0014).
- **Agents:** Google ADK (primary) + LangGraph (retained) behind `AgentFrameworkPort`; Vertex AI Gemini (`gemini-2.5-flash`), keyless.
- **Tools:** MCP servers as HTTP microservices (ADR-0015).
- **Data:** Firestore (state) + BigQuery (analytical, later) behind ports (ADR-0004).
- **Cloud/CI:** GCP (Cloud Run, Artifact Registry, Secret Manager); Terraform; keyless WIF deploys.

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
docs/          # product, requirements, architecture, implementation, design, adr, runbooks, phase-closure, learnings
.github/workflows/  # ci.yml + deploy-dev.yml (keyless) + gcp-auth-check.yml
docker-compose.yml  # local market-data MCP
```

## Development

`uv run` for tests uses `pythonpath` from `pyproject.toml` (`.` and `mcp_servers/`). For `uvicorn`, set `PYTHONPATH=.` from the repo root.

```
uv sync                                   # install toolchain + deps
uv run ruff check . && uv run mypy core api adapters mcp_servers tests
uv run pytest -m "not integration" --cov  # unit tests + coverage (default CI unit job)
docker compose up market-data-mcp --build # market-data MCP on http://localhost:8081
```

Backend switches (see `.env.example`):

| Variable | Values | Default |
|---|---|---|
| `PCOPILOT_AUTH_BACKEND` | `fake` \| `firebase` | `fake` |
| `PCOPILOT_REPO_BACKEND` | `memory` \| `firestore` | `memory` |
| `PCOPILOT_ANALYSIS_BACKEND` | `adk` \| `fake` | `adk` |

Local API + real Google Sign-In (authorized JS origin `http://localhost:8000`):

```
# Copy .env.example → .env and fill PCOPILOT_FIREBASE_*.
PCOPILOT_AUTH_BACKEND=firebase \
PCOPILOT_REPO_BACKEND=firestore \
PCOPILOT_ANALYSIS_BACKEND=adk \
PCOPILOT_MARKET_DATA_MCP_URL=http://localhost:8081/mcp \
PCOPILOT_FIREBASE_API_KEY=... \
PCOPILOT_FIREBASE_AUTH_DOMAIN=... \
PCOPILOT_FIREBASE_PROJECT_ID=... \
PYTHONPATH=. uv run uvicorn api.main:app --reload --port 8000
# open http://localhost:8000
```

After `gcloud auth application-default login`, **fully restart** the API process. `--reload` does not pick up new ADC (see [learning 0005](docs/learnings/0005-adc-restart-required.md)).

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

   If `FIRESTORE_EMULATOR_HOST` is unset, Firestore integration tests **skip**.

2. **MCP HTTP** — in-process HTTP server with a **fake** market-data provider (no yfinance). Included in `pytest -m integration`.

CI runs integration in a dedicated job (emulator + `pytest -m integration`).

Environment setup for a fresh GCP project: `docs/runbooks/environment-setup.md`.

## Deploy

Push to `main` (or `workflow_dispatch`) runs [`.github/workflows/deploy-dev.yml`](.github/workflows/deploy-dev.yml):

1. Build + push **market-data-mcp** → Cloud Run **private** (`mcp-run` SA).
2. Capture `status.url`, then build + push **api** → Cloud Run **public** (`run-app` SA) with `PCOPILOT_MARKET_DATA_MCP_URL=<mcp-url>/mcp` (https ⇒ ID-token auth, 2.7.3).
3. Smoke `GET /health` and `GET /config`.

Region: `asia-south1`. Images: `asia-south1-docker.pkg.dev/pcopilot-dev/containers/{api,market-data-mcp}`.

## Documentation

```
docs/
├── STATUS.md         # Current phase / handoff (resume here)
├── backlog.md        # F/A/O traceability
├── phase-closure/    # Per-phase closure reports (§7.9)
├── learnings/        # Numbered learnings (ADR-style)
├── product/          # One-Pager
├── requirements/     # PRD
├── architecture/     # Technical architecture
├── implementation/   # Phased roadmap
├── design/           # Design notes
├── runbooks/         # Operational runbooks
└── adr/              # ADRs
```

| Document | Description |
|---|---|
| [STATUS](docs/STATUS.md) | Phase handoff — start here in a new conversation |
| [Backlog](docs/backlog.md) | Requirement / infra traceability |
| [Phase closure](docs/phase-closure/) | Closure reports for Phases 0–2 |
| [Learnings](docs/learnings/) | Numbered lessons (0001–0005) |
| [One-Pager](docs/product/Portfolio-Copilot-One-Pager.md) | Problem, concept, agent architecture, stack, guardrails |
| [Requirements](docs/requirements/Portfolio-Copilot-Requirements.md) | PRD (draft v0.4) |
| [Architecture](docs/architecture/Portfolio-Copilot-Architecture.md) | C4, agents, MCP, data, deployment (draft v0.1) |
| [Implementation Phases](docs/implementation/Portfolio-Copilot-Implementation-Phases.md) | Phased, PR-gated roadmap (draft v0.1) |
| [ADRs](docs/adr/README.md) | ADRs 0001–0015 (0012 accepted: ADK primary) |
| [Design: framework spike](docs/design/framework-spike-comparison.md) | ADK vs LangGraph head-to-head |

Engineering methodology: **Multi-Agent Engineering Protocol v4.3** (`chandra-prompts` repo) — Strategist / Coordinator / Worker / Reviewer, PR-gated, one sub-phase per PR; phase-closure + learnings per §7.9.
