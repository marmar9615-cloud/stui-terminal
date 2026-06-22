from __future__ import annotations

import argparse
import tarfile
import zipfile
from collections.abc import Sequence
from pathlib import Path

FORBIDDEN_PARTS = {
    ".DS_Store",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "tests",
}

FORBIDDEN_SUFFIXES = {
    "docs/announcement-drafts.md",
}

WHEEL_REQUIRED_SUFFIXES = {
    "stui/__init__.py",
    "stui/api.py",
    "stui/app.py",
    "stui/cli.py",
    "stui/runtime.py",
    "stui/examples/basic.py",
    "stui/examples/counter.py",
    "stui/examples/model_demo.py",
    "stui/examples/inputs.py",
    "stui/examples/data_display.py",
    "stui/examples/dashboard.py",
    "stui/examples/forms.py",
    "stui/examples/layouts.py",
    "stui/examples/charts.py",
    "stui/examples/kitchen_sink.py",
    "dist-info/METADATA",
    "dist-info/WHEEL",
    "dist-info/entry_points.txt",
    "dist-info/licenses/LICENSE",
}

SDIST_REQUIRED_SUFFIXES = {
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "MANIFEST.in",
    "pyproject.toml",
    "docs/releases/README.md",
    "docs/terminal-compatibility.md",
    "assets/stui-model-demo.png",
    "examples/basic.py",
    "scripts/check.sh",
    "scripts/verify_custom_project.sh",
    "scripts/audit_package_contents.py",
    "src/stui/cli.py",
    "src/stui/examples/basic.py",
}


def _names_from_wheel(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def _names_from_sdist(path: Path) -> list[str]:
    with tarfile.open(path) as archive:
        return archive.getnames()


def _has_suffix(names: list[str], suffix: str) -> bool:
    return any(name.endswith(suffix) for name in names)


def _forbidden_names(names: list[str]) -> list[str]:
    forbidden: list[str] = []
    for name in names:
        parts = set(Path(name).parts)
        if parts & FORBIDDEN_PARTS or any(
            name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES
        ):
            forbidden.append(name)
    return forbidden


def _check_archive(path: Path, required_suffixes: set[str]) -> list[str]:
    if path.suffix == ".whl":
        names = _names_from_wheel(path)
    elif path.name.endswith(".tar.gz"):
        names = _names_from_sdist(path)
    else:
        return [f"unsupported distribution file: {path}"]

    errors = [
        f"{path.name}: missing required path ending in {suffix}"
        for suffix in sorted(required_suffixes)
        if not _has_suffix(names, suffix)
    ]
    errors.extend(
        f"{path.name}: forbidden package path {name}"
        for name in _forbidden_names(names)
    )
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit stui-terminal wheel and sdist contents."
    )
    parser.add_argument(
        "dist",
        nargs="?",
        default="dist",
        help="Directory containing built distributions.",
    )
    args = parser.parse_args(argv)

    dist_dir = Path(args.dist)
    wheel = sorted(dist_dir.glob("stui_terminal-*.whl"))
    sdist = sorted(dist_dir.glob("stui_terminal-*.tar.gz"))
    errors: list[str] = []
    if len(wheel) != 1:
        errors.append(f"expected exactly one wheel in {dist_dir}, found {len(wheel)}")
    if len(sdist) != 1:
        errors.append(f"expected exactly one sdist in {dist_dir}, found {len(sdist)}")

    if wheel:
        errors.extend(_check_archive(wheel[0], WHEEL_REQUIRED_SUFFIXES))
    if sdist:
        errors.extend(_check_archive(sdist[0], SDIST_REQUIRED_SUFFIXES))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    for artifact in [*wheel, *sdist]:
        size_kib = artifact.stat().st_size / 1024
        print(f"OK {artifact.name}: {size_kib:.1f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
