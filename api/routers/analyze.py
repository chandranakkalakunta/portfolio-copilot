"""Analyze endpoint — ADK fundamental agent (auth-protected)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.deps import get_analysis_engine, get_current_user, get_recommendation_logger
from api.schemas import AnalyzeBody
from core.ports.agent_framework import AgentFrameworkPort, AnalysisRequest, AnalysisResult
from core.ports.auth import AuthenticatedUser
from core.tracking.service import RecommendationLogService

router = APIRouter(tags=["analyze"])


@router.post("/analyze")
async def analyze(
    body: AnalyzeBody,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    engine: Annotated[AgentFrameworkPort, Depends(get_analysis_engine)],
    rec_log: Annotated[RecommendationLogService, Depends(get_recommendation_logger)],
) -> AnalysisResult:
    """Run single-ticker fundamental analysis (cited note). Portfolio-fit is Phase 4."""
    result = await engine.analyze(AnalysisRequest(ticker=body.ticker.strip().upper()))
    await rec_log.log_from_analysis(result, user)
    return result
