# 0005 — ADC expiry requires a full API restart

## Context

Local API processes use Application Default Credentials for Vertex, Firestore, and (when configured) Firebase Admin. Developers refresh ADC with `gcloud auth application-default login`.

## What happened

Reloading uvicorn (`--reload`) does **not** pick up new ADC files. The process keeps the in-memory credentials from first start. After ADC expiry, analyze / Firestore calls fail until the API process is fully stopped and started again. Recorded in `docs/STATUS.md` local-dev gotchas.

## Lesson

ADC is loaded once at process start. File-watch reload is not a credential refresh.

## Rule

After `gcloud auth application-default login`, **fully restart** the API (kill the process; do not rely on `--reload`). Document this next to any local-run instructions.
