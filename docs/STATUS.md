# Project Status / Handoff

**Updated:** 14 August 2026
**Phase:** 2 — Walking skeleton ✓ COMPLETE

## How to resume in a fresh conversation (protocol §6.1)

Provide the new Strategist:
1. **Multi-Agent Engineering Protocol v4.3** (`chandra-prompts` repo).
2. **This repo** — the source of truth: `docs/requirements` (v0.4), `docs/architecture` (v0.1), `docs/adr` (0001–0015), `docs/implementation` (roadmap), `docs/backlog.md`, `docs/phase-closure/`, `docs/learnings/`, `CHANGELOG.md`, and this file.
3. The line: **"Phase 2 complete — ready to begin Phase 3."**

Worker = Grok CLI. One sub-phase per PR; pre-flight requires **no open PRs** (§0.1 #15). Phase-end **doc-hygiene** is mandatory (§7.8).

## Done
- **Phase 0** ✓ — repo/toolchain, CI, keyless WIF, Terraform, `hello` deployed to Cloud Run.
- **Phase 1** ✓ — ADK vs LangGraph spike; **ADK primary** (ADR-0012).
- **Phase 2** ✓ — walking skeleton deployed and verified end-to-end: market-data MCP (HTTP microservice), Firestore portfolio/profile domain, backend Google/Firebase token verification, cited fundamental note (ADK→MCP→Vertex), auth-protected API, minimal UI + **real Google Sign-In validated end-to-end** (sign in → save holding to Firestore → analyze → cited note), CI hardening (coverage + dep/secret scan), integration tests (Firestore emulator + MCP HTTP), IaC codification (APIs + Firestore in Terraform), Dockerfile bundles core/adapters (2.7.1), runtime IAM applied (2.7.2), lazy heavy imports + MCP service-to-service ID-token auth (2.7.3), **two Cloud Run services** (2.7.4) — `api` public + `market-data-mcp` private; DRS exception on `pcopilot-dev`; Firebase authorized domain for the API host.
- **Live e2e (2026-08-14):** signed in (Firebase Google) → saved an NVDA holding to Firestore → analyzed a ticker → cited note rendered with market-data MCP citations (`as_of`) + disclaimer. API logs: `POST /portfolios`, `POST /positions`, `POST /analyze`, `GET /me` all 200.

## Next (Phase 3)
- **Phase 3 — Valuation, Performance & Recommendation Logging** (F10–F14, F29). Sub-phase breakdown is produced at build time (protocol §2.1).

## Key facts
- **Live API URL:** https://api-552451662981.asia-south1.run.app
- **GCP project:** `pcopilot-dev` (number 552451662981), region **asia-south1**; Firestore (default, native, asia-south1) in Terraform.
- **Firebase Auth project:** `pcopilot-dev-d0a08` (separate) — API verifies tokens against `PCOPILOT_FIREBASE_PROJECT_ID`; Firestore/Vertex use `pcopilot-dev`.
- **LLM:** Vertex Gemini `gemini-2.5-flash` @ **us-central1** (Gemini not in asia-south1).
- **WIF/SAs:** `gh-deployer` (deploy; `roles/run.admin`), `run-app` (API runtime), `mcp-run` (MCP runtime, no roles). Provider: `projects/552451662981/locations/global/workloadIdentityPools/github-pool/providers/github-provider`.
- **Config switches:** `PCOPILOT_AUTH_BACKEND` (fake|firebase), `PCOPILOT_REPO_BACKEND` (memory|firestore), `PCOPILOT_ANALYSIS_BACKEND` (adk|fake).
- **Org policy:** DRS exception in place on staging (`iam.allowedPolicyMemberDomains` = `allowAll:true` on `pcopilot-dev`, 2026-08-14). Prod remains LB+NEG (backlog).

## Local-dev gotchas
- ADC expires: `gcloud auth application-default login` **and fully restart** the API process (in-memory creds don't refresh on reload).
- Run the market-data MCP from the repo dir: `docker compose up market-data-mcp --build`.
