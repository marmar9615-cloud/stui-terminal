from __future__ import annotations

import ast
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "stui"
PYPROJECT = ROOT / "pyproject.toml"

FORBIDDEN_DISTRIBUTIONS = {"streamlit", "textual-slider"}
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "fastapi",
    "flask",
    "http.server",
    "socket",
    "streamlit",
    "textual_slider",
    "uvicorn",
    "websocket",
    "websockets",
}


def _source_files() -> list[Path]:
    return sorted(path for path in SRC.rglob("*.py") if "__pycache__" not in path.parts)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    return imports


def test_runtime_dependencies_do_not_include_streamlit_or_slider_package() -> None:
    metadata = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    dependencies = metadata["project"].get("dependencies", [])

    normalized = {
        dependency.split(">", 1)[0].split("=", 1)[0]
        for dependency in dependencies
    }

    assert normalized.isdisjoint(FORBIDDEN_DISTRIBUTIONS)


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    violations: list[str] = []

    for path in _source_files():
        for module in _imported_modules(path):
            for forbidden in FORBIDDEN_IMPORT_ROOTS:
                if module == forbidden or module.startswith(f"{forbidden}."):
                    violations.append(
                        f"{path.relative_to(ROOT)} imports forbidden module {module}"
                    )

    assert violations == []


def test_source_does_not_use_forbidden_server_or_browser_terms() -> None:
    forbidden_terms = {
        "http.server",
        "port_forward",
        "port-forward",
        "socketserver",
        "textual_slider",
        "webbrowser",
        "websocket",
    }
    violations: list[str] = []

    for path in _source_files():
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            if term in text:
                violations.append(f"{path.relative_to(ROOT)} contains {term}")

    assert violations == []
