# 0004 — “Plan only” IaC drifts from reality

## Context

Phase 2.7.2 merged Terraform for runtime IAM as **plan only** (PR #28, 2026-08-14). Backlog/STATUS kept saying “Plan only / apply after review.” The Coordinator later applied the plan. Docs were not updated until Phase 2 doc-hygiene (PR #31).

## What happened

`gcloud get-iam-policy` on 2026-08-14 showed the IAM **was applied**: `run-app` had `roles/aiplatform.user`, `roles/datastore.user`, `roles/run.invoker`; `mcp-run` existed; `gh-deployer` had actAs on `mcp-run`. The repo still described it as unapplied. Hygiene had to reconcile the drift.

## Lesson

A “plan only” PR is a snapshot. Once someone applies, the living docs are wrong unless someone verifies cloud state and updates them.

## Rule

After any apply (or suspected apply), verify with `gcloud` / `terraform plan` (expect no-op) and immediately update `docs/backlog.md` + `docs/STATUS.md`. Do not treat CHANGELOG’s original “plan only” line as current state — CHANGELOG is append-only history.
