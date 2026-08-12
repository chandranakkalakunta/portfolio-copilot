# ADR-0006: Runtime reviewer agent (propose→review→gate)

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements A6, F26, F49–F51; architecture §7.2; mirrors protocol §1.6 at runtime

## Context

A single model reviewing its own analysis shares that output's blind spots. Recommendations must be grounded and cited (F26, A6) and must never over-claim or imply guarantees (F51). The user asked for Grok to act as a runtime "second eye" that reviews the work and flags issues before it reaches the user.

## Decision

Add a **runtime Reviewer agent** as the final stage of the analysis pipeline: the report-writer produces a rating + cited note, then an **independent, different-model** Reviewer (Grok, behind `LLMPort`) critiques it for unsupported claims, missing citations, over-confidence, and portfolio-fit errors. The orchestrator gates on the result: pass → surface to user + log; issues → loop back. The Reviewer has no authority to edit or approve autonomously — it advises; the pipeline/guardrails act. It is **config-toggleable** and applied by **depth/risk tier** (skipped in quick mode; on for deep mode) to bound latency and cost.

## Consequences

**Positive:** independent second-eye catches groundedness and over-claiming issues (A6); model-pluggable via `LLMPort`; aligns runtime quality control with the engineering protocol's review philosophy.

**Negative / cost:** extra latency and token cost per reviewed request; another model dependency; risk of loops if not bounded (cap review iterations).

**Follow-ups:** define the review rubric and severity tags; cap loop-backs; measure added latency/cost; evaluate reviewer efficacy against the eval harness (ADR-0004 data).

## Alternatives considered

- **Same-model self-critique.** Cheaper, but shares blind spots; weaker independence.
- **No reviewer, rely on report-writer + guardrails only.** Lower cost/latency but weaker groundedness assurance; rejected for deep/high-stakes analysis, retained as the quick-mode path.
