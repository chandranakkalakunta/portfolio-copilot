"""Guard: core/ must not import cloud SDKs (ADR-0001 / F55)."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_ROOTS = ("google.cloud", "boto3", "azure", "firebase_admin")


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module)
    return modules


def _is_forbidden(module: str) -> bool:
    return any(module == root or module.startswith(f"{root}.") for root in FORBIDDEN_ROOTS)


def test_core_imports_no_cloud_sdks() -> None:
    core_dir = Path(__file__).resolve().parents[1] / "core"
    offenders: list[str] = []
    for py_file in sorted(core_dir.rglob("*.py")):
        for module in _imported_modules(py_file):
            if _is_forbidden(module):
                offenders.append(f"{py_file.relative_to(core_dir.parent)}: {module}")
    assert offenders == [], f"Cloud SDK imports found in core/: {offenders}"
