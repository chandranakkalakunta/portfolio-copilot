# Portfolio Copilot

An AI equity-research analyst that knows your portfolio. Built on an agentic framework (Google ADK) and MCP, it produces cited, personalized buy / sell / trim ideas — for both existing positions and new stocks — across US and Indian markets.

> **Not investment advice.** All outputs are informational; the user is solely responsible for their own due diligence and decisions. Display-only — never executes real trades.

## Documentation

```
docs/
├── product/          # Vision and positioning
│   └── Portfolio-Copilot-One-Pager.md
├── requirements/     # Functional & non-functional requirements
│   └── Portfolio-Copilot-Requirements.md
├── architecture/     # System design, agents, MCP, data model (planned)
├── design/           # Detailed design notes (planned)
└── adr/              # Architecture Decision Records (planned)
```

| Document | Description |
|---|---|
| [One-Pager](docs/product/Portfolio-Copilot-One-Pager.md) | Problem, concept, agent architecture, stack, guardrails |
| [Requirements](docs/requirements/Portfolio-Copilot-Requirements.md) | Detailed PRD — goals, use cases, FRs/NFRs (draft v0.2) |

## Status

Early product definition. Requirements are **draft v0.2** for review; architecture and implementation are not started.

v0.2 adds PWA (F53), modularity/pluggability (§6.12, F54–F57), internet-scale scalability as P0, and open-source/free-first sourcing.
