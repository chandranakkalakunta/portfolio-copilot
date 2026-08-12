"""Live ADK spike smoke: one analyze("AAPL") against Vertex Gemini via ADC."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow running without editable install of adapters/
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from adapters.agent_adk.engine import AdkAnalysisEngine
from core.ports.agent_framework import AnalysisRequest


async def main() -> None:
    engine = AdkAnalysisEngine()
    result = await engine.analyze(AnalysisRequest(ticker="AAPL"))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
