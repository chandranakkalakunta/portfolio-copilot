"""Provider-agnostic agent-framework port (ADR-0001, ADR-0012).

ADK and LangGraph adapters each implement ``analyze()``. The ``framework`` field
on results records which adapter produced the result (attribution).
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field

DEFAULT_DISCLAIMER = (
    "Not investment advice. All outputs are informational; the user is solely "
    "responsible for their own due diligence and decisions. Display-only — "
    "never executes real trades."
)


class AnalysisRequest(BaseModel):
    """Input to a framework adapter analysis run."""

    ticker: str


class Citation(BaseModel):
    """Attribution for a figure used in the analysis (source + as-of)."""

    source: str
    as_of: str
    detail: str


class AnalysisResult(BaseModel):
    """Output of a framework adapter analysis run."""

    ticker: str
    summary: str
    tool_calls: list[str]
    framework: str
    citations: list[Citation] = Field(default_factory=list)
    disclaimer: str = DEFAULT_DISCLAIMER
    # Skeleton label; full trim/add/hold/sell + portfolio-fit arrive in Phase 4.
    rating: str = "informational"


class AgentFrameworkPort(Protocol):
    """Provider-agnostic port for agent-framework analysis (ADR-0001, ADR-0012).

    ADK and LangGraph adapters each implement ``analyze()``.
    """

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run analysis for the given request and return a structured result."""
        ...
