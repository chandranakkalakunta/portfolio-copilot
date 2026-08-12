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
├── architecture/     # System design, agents, MCP, data model
│   └── Portfolio-Copilot-Architecture.md
├── design/           # Detailed design notes (planned)
└── adr/              # Architecture Decision Records (planned)
```

| Document | Description |
|---|---|
| [One-Pager](docs/product/Portfolio-Copilot-One-Pager.md) | Problem, concept, agent architecture, stack, guardrails |
| [Requirements](docs/requirements/Portfolio-Copilot-Requirements.md) | Detailed PRD — goals, use cases, FRs/NFRs (draft v0.2) |
| [Architecture](docs/architecture/Portfolio-Copilot-Architecture.md) | Technical architecture — C4, agents, MCP, data, deployment (draft v0.1) |

## Status

Early product definition. Requirements **draft v0.2** and architecture **draft v0.1** are in review; implementation is not started.

Requirements v0.2 adds PWA (F53), modularity/pluggability (§6.12, F54–F57), internet-scale scalability as P0, and open-source/free-first sourcing.
