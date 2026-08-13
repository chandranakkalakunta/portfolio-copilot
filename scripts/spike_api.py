"""API smoke: fake-auth portfolio CRUD + LIVE /analyze (MCP + Vertex).

Prereqs:
  - market-data MCP on :8081
  - API with PCOPILOT_AUTH_BACKEND=fake PCOPILOT_REPO_BACKEND=memory
  - ADC for Vertex when hitting real /analyze
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from adapters.fake_auth.auth import FAKE_VALID_TOKEN

API_BASE = os.environ.get("PCOPILOT_API_URL", "http://127.0.0.1:8000")


def main() -> None:
    headers = {"Authorization": f"Bearer {FAKE_VALID_TOKEN}"}
    with httpx.Client(base_url=API_BASE, timeout=120.0) as client:
        print("=== health ===")
        print(client.get("/health").json())

        print("=== create portfolio ===")
        pf = client.post(
            "/portfolios",
            headers=headers,
            json={"id": "spike-pf-api", "type": "paper", "market": "US", "cash": 10000},
        )
        pf.raise_for_status()
        print(json.dumps(pf.json(), indent=2))

        print("=== add position ===")
        pos = client.post(
            "/portfolios/spike-pf-api/positions",
            headers=headers,
            json={
                "ticker": "AAPL",
                "quantity": 5,
                "cost_basis": 180.0,
                "acquired": "2024-03-01",
            },
        )
        pos.raise_for_status()
        print(json.dumps(pos.json(), indent=2, default=str))

        print("=== get portfolio ===")
        got = client.get("/portfolios/spike-pf-api", headers=headers)
        got.raise_for_status()
        print(json.dumps(got.json(), indent=2))

        print("=== list positions ===")
        listed = client.get("/portfolios/spike-pf-api/positions", headers=headers)
        listed.raise_for_status()
        print(json.dumps(listed.json(), indent=2, default=str))

        print("=== LIVE /analyze AAPL ===")
        note = client.post("/analyze", headers=headers, json={"ticker": "AAPL"})
        note.raise_for_status()
        print(json.dumps(note.json(), indent=2))


if __name__ == "__main__":
    main()
