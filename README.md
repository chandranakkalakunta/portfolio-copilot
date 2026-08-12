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
└── adr/              # Architecture Decision Records (0001–0012)
    ├── README.md     # ADR index
    └── NNNN-*.md     # One file per decision
```

| Document | Description |
|---|---|
| [One-Pager](docs/product/Portfolio-Copilot-One-Pager.md) | Problem, concept, agent architecture, stack, guardrails |
| [Requirements](docs/requirements/Portfolio-Copilot-Requirements.md) | Detailed PRD — goals, use cases, FRs/NFRs + operational/platform requirements (draft v0.3.1) |
| [Architecture](docs/architecture/Portfolio-Copilot-Architecture.md) | Technical architecture — C4, agents, MCP, data, deployment (draft v0.1) |
| [ADRs](docs/adr/README.md) | Architecture Decision Records 0001–0012 (0012 proposed, pending framework spike) |

## Status

Early product definition. Requirements **draft v0.3.1** and architecture **draft v0.1** are in review; implementation is not started. ADRs **0001–0012** record the foundational decisions (0012 — agent framework — is *proposed*, pending a hands-on ADK vs LangGraph spike).

Requirements v0.3 broadens coverage to the full functional + non-functional gamut: identity & access (F58–F62), notifications (F63–F65), and a detailed operational/platform section §11 (CI/CD, environments/IaC, testing & QA, availability/SLOs, disaster recovery & backup, incident response, data lifecycle & governance, rate limiting, accessibility & i18n, maintainability). Earlier v0.2 added PWA, modularity/pluggability, internet-scale scalability, and open-source/free-first sourcing.
