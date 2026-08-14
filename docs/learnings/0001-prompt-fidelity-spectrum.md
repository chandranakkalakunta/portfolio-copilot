# 0001 — Prompt fidelity spectrum

## Context

Phase 2 Worker prompts mixed styles. Most sub-phases (2.6–2.7.3) pinned **outcomes and constraints**. 2.7.4 pasted an entire `deploy-dev.yml` and forbade architectural decisions. A terminal control sequence (`public` + CSI junk) even landed in the prompt text.

## What happened

The verbatim deploy workflow was the right call for a risk-sensitive CD file (one wrong `gcloud` flag is an outage). It also blocked the Worker from matching repo style or fixing adjacent issues except as notes. The 2.7.4 retro: pin character-exact text only where a single character is an outage or a security boundary.

## Lesson

Treat prompt fidelity as a spectrum, not a single “be exact” rule.

## Rule

- **Verbatim** — IAM HCL, gcloud flags, secret names, service/SA names: one character can be an outage or a security miss.
- **Contract** — deploy/CI shape (order, public/private, env vars): pin the contract; let the Worker author YAML to repo style.
- **Outcomes** — low-risk app/docs work: pin goals, tests, and “never do X”; do not paste the patch.
