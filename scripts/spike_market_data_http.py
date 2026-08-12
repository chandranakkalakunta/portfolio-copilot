"""LIVE smoke: call market-data MCP get_quote over HTTP (server must be running)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import MCPSettings
from mcp import Client


def _tool_result_payload(result: Any) -> Any:
    """Best-effort extract structured/tool payload from CallToolResult."""
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    content = getattr(result, "content", None)
    if content:
        texts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                texts.append(text)
        if len(texts) == 1:
            try:
                return json.loads(texts[0])
            except json.JSONDecodeError:
                return texts[0]
        if texts:
            return texts
    return result


async def main() -> None:
    settings = MCPSettings()
    url = settings.market_data_mcp_url
    print(f"Connecting to MCP at {url}", flush=True)
    async with Client(url) as client:
        result = await client.call_tool("get_quote", {"ticker": "AAPL"})
        payload = _tool_result_payload(result)
        print(
            json.dumps(
                {"tool": "get_quote", "ticker": "AAPL", "result": payload}, indent=2, default=str
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
