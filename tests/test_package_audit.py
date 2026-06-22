from __future__ import annotations

import importlib.util
import tarfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_package_contents.py"
SPEC = importlib.util.spec_from_file_location("audit_package_contents", SCRIPT)
assert SPEC is not None
audit_package_contents = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit_package_contents)


def _write_wheel(path: Path, names: set[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, "")


def _write_sdist(path: Path, names: set[str]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name in names:
            temp = path.parent / Path(name).name
            temp.write_text("", encoding="utf-8")
            archive.add(temp, arcname=name)
            temp.unlink()


def _prefixed(prefix: str, suffixes: Iterable[str]) -> set[str]:
    return {f"{prefix}/{suffix}" for suffix in suffixes}


def test_package_audit_accepts_expected_wheel_and_sdist(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"

    _write_wheel(
        wheel,
        _prefixed("pkg", audit_package_contents.WHEEL_REQUIRED_SUFFIXES),
    )
    _write_sdist(
        sdist,
        _prefixed(
            "stui_terminal-1.3.0",
            audit_package_contents.SDIST_REQUIRED_SUFFIXES,
        ),
    )

    assert audit_package_contents.main([str(tmp_path)]) == 0


def test_package_audit_rejects_forbidden_paths(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"

    _write_wheel(
        wheel,
        {
            *_prefixed("pkg", audit_package_contents.WHEEL_REQUIRED_SUFFIXES),
            "pkg/tests/test_leak.py",
        },
    )
    _write_sdist(
        sdist,
        {
            *_prefixed(
                "stui_terminal-1.3.0",
                audit_package_contents.SDIST_REQUIRED_SUFFIXES,
            ),
            "stui_terminal-1.3.0/.venv/pyvenv.cfg",
            "stui_terminal-1.3.0/docs/announcement-drafts.md",
        },
    )

    assert audit_package_contents.main([str(tmp_path)]) == 1
