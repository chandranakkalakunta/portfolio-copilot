"""Importing api.main must not load ADK / LangGraph / Vertex (cold-start)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_HEAVY = (
    "google.adk",
    "langgraph",
    "langchain_google_vertexai",
    "vertexai",
)


def test_import_api_main_does_not_load_heavy_sdks() -> None:
    """Subprocess so other tests that import adapters cannot pollute sys.modules."""
    script = (
        "import sys\n"
        "import api.main  # noqa: F401\n"
        f"heavy = {list(_HEAVY)!r}\n"
        "found = [\n"
        "    name for name in heavy\n"
        "    if name in sys.modules\n"
        "    or any(mod == name or mod.startswith(name + '.') for mod in sys.modules)\n"
        "]\n"
        "assert not found, found\n"
    )
    env_pythonpath = str(_ROOT)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": env_pythonpath},
    )
    assert result.returncode == 0, result.stdout + result.stderr
