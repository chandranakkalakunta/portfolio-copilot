# 0002 — Public Cloud Run needs `run.admin`

## Context

`gh-deployer` originally held `roles/run.developer` (Phase 0.3.1). PR #30’s `deploy-dev.yml` deploys the API with `--allow-unauthenticated`, which writes an `allUsers` IAM binding on the Cloud Run service.

## What happened

Claude’s review of PR #30 (blocker B1): `run.developer` does **not** include `run.services.setIamPolicy`. The public API deploy would fail at the IAM step. The amend (`a6105d6`) renamed the Terraform member to `deployer_run_admin` and granted `roles/run.admin`.

## Lesson

Making a Cloud Run service public is an IAM-policy write, not just a deploy. Developer is not enough.

## Rule

A deployer that must set `allUsers` (or any invoker binding) on Cloud Run needs `roles/run.admin` (or an equivalent that includes `setIamPolicy`). Re-tighten to `run.developer` + service-scoped invoker management before prod (backlog).
