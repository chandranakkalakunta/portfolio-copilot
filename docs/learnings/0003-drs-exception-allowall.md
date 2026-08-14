# 0003 — DRS exception for public staging ingress

## Context

The org’s Domain Restricted Sharing policy blocks `allUsers` / `allAuthenticatedUsers`. A public Cloud Run URL for the walking-skeleton UI needs that binding.

## What happened

On 2026-08-14 (~11:47 UTC) the Coordinator set `iam.allowedPolicyMemberDomains` = `allowAll:true` on project `pcopilot-dev`. Combined with `gh-deployer` `run.admin`, `--allow-unauthenticated` on `api` succeeded. Browser Google Sign-In then worked after the API host was added to Firebase authorized domains.

## Lesson

Public Cloud Run under DRS fails even with the right SA roles until the **org policy** allows the member. Staging used a project-level `allowAll` exception; that is not the prod posture.

## Rule

Staging: project DRS exception (`allowAll:true`) is acceptable for a short-lived public API. Prod: keep Cloud Run private; expose via HTTPS LB + Serverless NEG (backlog). Re-tighten DRS after staging.
