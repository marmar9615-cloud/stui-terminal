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


def test_v220_package_files_are_required() -> None:
    assert {
        "stui/_terminal_text.py",
        "stui/cache.py",
        "stui/examples/caching.py",
        "stui/examples/prompt_workbench.py",
    }.issubset(audit_package_contents.WHEEL_REQUIRED_SUFFIXES)
    assert {
        "examples/caching.py",
        "examples/prompt_workbench.py",
        "src/stui/_terminal_text.py",
        "src/stui/cache.py",
        "src/stui/examples/caching.py",
        "src/stui/examples/prompt_workbench.py",
    }.issubset(audit_package_contents.SDIST_REQUIRED_SUFFIXES)


def _write_wheel(path: Path, names: set[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            if name.endswith("/METADATA"):
                archive.writestr(name, "Metadata-Version: 2.4\nVersion: 1.3.0\n")
            elif name.endswith("/entry_points.txt"):
                archive.writestr(name, "[console_scripts]\nstui = stui.cli:app\n")
            else:
                archive.writestr(name, "")


def _write_sdist(path: Path, names: set[str]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name in names:
            temp = path.parent / Path(name).name
            if name.endswith("PKG-INFO"):
                temp.write_text(
                    "Metadata-Version: 2.4\nVersion: 1.3.0\n",
                    encoding="utf-8",
                )
            else:
                temp.write_text("", encoding="utf-8")
            archive.add(temp, arcname=name)
            temp.unlink()


def _prefixed(prefix: str, suffixes: Iterable[str]) -> set[str]:
    return {f"{prefix}/{suffix}" for suffix in suffixes}


def _wheel_names(version: str = "1.3.0") -> set[str]:
    dist_info = f"stui_terminal-{version}.dist-info"
    return {
        f"{dist_info}/{suffix.removeprefix('dist-info/')}"
        if suffix.startswith("dist-info/")
        else suffix
        for suffix in audit_package_contents.WHEEL_REQUIRED_SUFFIXES
    }


def _sdist_names(version: str = "1.3.0") -> set[str]:
    root = f"stui_terminal-{version}"
    return {
        *_prefixed(root, audit_package_contents.SDIST_REQUIRED_SUFFIXES),
        f"{root}/PKG-INFO",
    }


def test_package_audit_accepts_expected_wheel_and_sdist(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"

    _write_wheel(wheel, _wheel_names())
    _write_sdist(sdist, _sdist_names())

    assert audit_package_contents.main([str(tmp_path)]) == 0
    assert audit_package_contents.main([str(tmp_path), "--version", "1.3.0"]) == 0


def test_package_audit_rejects_forbidden_paths(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"

    _write_wheel(
        wheel,
        {
            *_wheel_names(),
            "pkg/tests/test_leak.py",
        },
    )
    _write_sdist(
        sdist,
        {
            *_sdist_names(),
            "stui_terminal-1.3.0/.venv/pyvenv.cfg",
            "stui_terminal-1.3.0/docs/announcement-drafts.md",
        },
    )

    assert audit_package_contents.main([str(tmp_path)]) == 1


def test_package_audit_rejects_wrong_expected_version(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"

    _write_wheel(wheel, _wheel_names())
    _write_sdist(sdist, _sdist_names())

    assert audit_package_contents.main([str(tmp_path), "--version", "1.8.0"]) == 1


def test_package_audit_rejects_missing_console_entry_point(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"
    names = _wheel_names()

    with zipfile.ZipFile(wheel, "w") as archive:
        for name in names:
            if name.endswith("/METADATA"):
                archive.writestr(name, "Metadata-Version: 2.4\nVersion: 1.3.0\n")
            elif name.endswith("/entry_points.txt"):
                archive.writestr(name, "[console_scripts]\nother = stui.cli:app\n")
            else:
                archive.writestr(name, "")
    _write_sdist(sdist, _sdist_names())

    assert audit_package_contents.main([str(tmp_path), "--version", "1.3.0"]) == 1


def test_package_audit_rejects_misplaced_required_path_decoys(tmp_path: Path) -> None:
    wheel = tmp_path / "stui_terminal-1.3.0-py3-none-any.whl"
    sdist = tmp_path / "stui_terminal-1.3.0.tar.gz"
    wheel_names = _wheel_names()
    wheel_names.remove("stui/cache.py")
    wheel_names.add("decoy/stui/cache.py")
    sdist_names = _sdist_names()
    sdist_names.remove("stui_terminal-1.3.0/src/stui/cache.py")
    sdist_names.add("stui_terminal-1.3.0/decoy/src/stui/cache.py")

    _write_wheel(wheel, wheel_names)
    _write_sdist(sdist, sdist_names)

    assert audit_package_contents.main([str(tmp_path), "--version", "1.3.0"]) == 1
