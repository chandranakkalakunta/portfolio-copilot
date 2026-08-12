"""Provider-agnostic agent-framework port (ADR-0001, ADR-0012).

ADK and LangGraph adapters each implement ``analyze()``. The ``framework`` field
on results records which adapter produced the result (attribution).
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    """Input to a framework adapter analysis run."""

    ticker: str


class AnalysisResult(BaseModel):
    """Output of a framework adapter analysis run."""

    ticker: str
    summary: str
    tool_calls: list[str]
    framework: str


class AgentFrameworkPort(Protocol):
    """Provider-agnostic port for agent-framework analysis (ADR-0001, ADR-0012).

    ADK and LangGraph adapters each implement ``analyze()``.
    """

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run analysis for the given request and return a structured result."""
        ...
