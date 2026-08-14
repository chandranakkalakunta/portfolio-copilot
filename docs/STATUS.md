# Project Status / Handoff

**Updated:** 14 August 2026
**Phase:** 2 — Walking skeleton (in progress)

## How to resume in a fresh conversation (protocol §6.1)

Provide the new Strategist:
1. **Multi-Agent Engineering Protocol v4.2** (`chandra-prompts` repo).
2. **This repo** — the source of truth: `docs/requirements` (v0.4), `docs/architecture` (v0.1), `docs/adr` (0001–0015), `docs/implementation` (roadmap), `docs/backlog.md`, `CHANGELOG.md`, and this file.
3. The line: **"Ready for sub-phase 2.7.4"** (or whichever is next).

Worker = Grok CLI. One sub-phase per PR; pre-flight requires **no open PRs** (§0.1 #15). Phase-end **doc-hygiene** is mandatory (§7.8).

## Done
- **Phase 0** ✓ — repo/toolchain, CI, keyless WIF, Terraform, `hello` deployed to Cloud Run.
- **Phase 1** ✓ — ADK vs LangGraph spike; **ADK primary** (ADR-0012).
- **Phase 2 so far**: market-data MCP (HTTP microservice), Firestore portfolio/profile domain, backend Google/Firebase token verification, cited fundamental note (ADK→MCP→Vertex), auth-protected API, minimal UI + **real Google Sign-In validated end-to-end** (sign in → save holding to Firestore → analyze → cited note), CI hardening (coverage + dep/secret scan), integration tests (Firestore emulator + MCP HTTP), IaC codification (APIs + Firestore in Terraform), Dockerfile bundles core/adapters (2.7.1), runtime IAM plan (2.7.2), lazy heavy imports + MCP service-to-service ID-token auth (2.7.3).

## Next (Phase 2)
- **2.7.4** — deploy pipeline → **API** + **market-data MCP** as two Cloud Run services (`--cpu-boost`, longer startup timeout, real Firebase/Firestore/MCP-URL config); **DRS org-policy exception** on `pcopilot-dev` for browser access (Coordinator, org-admin); add the Cloud Run URL to **Firebase authorized domains**; deployed smoke.
- **Phase-2 doc-hygiene** (§7.8) → then Phase 2 complete.

## Key facts
- **GCP project:** `pcopilot-dev` (number 552451662981), region **asia-south1**; Firestore (default, native, asia-south1) in Terraform.
- **Firebase Auth project:** `pcopilot-dev-d0a08` (separate) — API verifies tokens against `PCOPILOT_FIREBASE_PROJECT_ID`; Firestore/Vertex use `pcopilot-dev`.
- **LLM:** Vertex Gemini `gemini-2.5-flash` @ **us-central1** (Gemini not in asia-south1).
- **WIF/SAs:** `gh-deployer` (deploy), `run-app` (API runtime), `mcp-run` (MCP runtime, no roles). Provider: `projects/552451662981/locations/global/workloadIdentityPools/github-pool/providers/github-provider`.
- **Config switches:** `PCOPILOT_AUTH_BACKEND` (fake|firebase), `PCOPILOT_REPO_BACKEND` (memory|firestore), `PCOPILOT_ANALYSIS_BACKEND` (adk|fake).
- **Org policy:** Domain-Restricted Sharing blocks `allUsers` — public ingress needs a DRS exception (staging) or LB+NEG (prod, backlog).

## Local-dev gotchas
- ADC expires: `gcloud auth application-default login` **and fully restart** the API process (in-memory creds don't refresh on reload).
- Run the market-data MCP from the repo dir: `docker compose up market-data-mcp --build`.
