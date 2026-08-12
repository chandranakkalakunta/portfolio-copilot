# ADR-0008: Prompt-injection / guardrail approach for ingested content

- **Status:** Accepted (2026-08-11)
- **Deciders:** Coordinator (Chandra), Strategist
- **Related:** requirements A2, F50, F49, F51, F52; architecture §7.3, §13

## Context

Agents ingest external, untrusted content — filings, news articles, web/social text — which can contain adversarial instructions ("ignore previous instructions", fake directives). If an agent treats ingested text as instructions, it can be manipulated into unsafe, ungrounded, or off-policy output. The product also must never imply guarantees or execution (F51) and must always disclaim (F49).

## Decision

Treat **all tool/MCP output as data, never instructions** (A2, F50). Structural defenses: (1) clear separation in prompts between trusted instructions and untrusted retrieved content (delimited, labeled as data); (2) agents act only on their defined task and tool schemas, not on directives found in content; (3) the **Reviewer agent** (ADR-0006) and guardrail/policy layer check outputs for groundedness (A6), over-claiming, guarantee/execution language (F51), and off-scope drift (F52); (4) mandatory disclaimer on every output (F49). Guardrails live in the service/policy layer, reachable by all entry points (protocol §5.16), not in the transport layer.

## Consequences

**Positive:** resilience to prompt-injection via ingested content; consistent policy enforcement across UI and any future API entry point; truthful, disclaimed, grounded outputs.

**Negative / cost:** some added prompt complexity and review overhead; no guardrail is perfect — defense-in-depth reduces but does not eliminate risk.

**Follow-ups:** define the delimiting/labeling convention; build a red-team eval set of injection attempts into the eval harness; log guardrail triggers.

## Alternatives considered

- **Trust ingested content implicitly.** Unacceptable — direct injection risk; rejected.
- **Single output filter only (no structural separation).** Weaker; injection can still corrupt reasoning before the filter. Defense-in-depth (structure + review + filter) chosen instead.
