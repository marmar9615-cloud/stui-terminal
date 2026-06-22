from __future__ import annotations

import argparse
import email.parser
import re
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
    "scripts/benchmark_runtime.py",
    "src/stui/cli.py",
    "src/stui/examples/basic.py",
}

ENTRY_POINT = "stui = stui.cli:app"


def _names_from_wheel(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def _names_from_sdist(path: Path) -> list[str]:
    with tarfile.open(path) as archive:
        return archive.getnames()


def _has_suffix(names: list[str], suffix: str) -> bool:
    return any(name.endswith(suffix) for name in names)


def _unsafe_names(names: list[str]) -> list[str]:
    unsafe: list[str] = []
    seen: set[str] = set()
    for name in names:
        path = Path(name)
        if name.startswith("/") or ".." in path.parts:
            unsafe.append(name)
        if name in seen:
            unsafe.append(name)
        seen.add(name)
    return unsafe


def _forbidden_names(names: list[str]) -> list[str]:
    forbidden: list[str] = []
    for name in names:
        parts = set(Path(name).parts)
        if parts & FORBIDDEN_PARTS or any(
            name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES
        ):
            forbidden.append(name)
    return forbidden


def _dist_info_prefix(names: list[str]) -> str | None:
    prefixes = {
        "/".join(Path(name).parts[:1])
        for name in names
        if Path(name).parts and Path(name).parts[0].endswith(".dist-info")
    }
    if len(prefixes) != 1:
        return None
    return next(iter(prefixes))


def _read_wheel_text(path: Path, name: str) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read(name).decode("utf-8")


def _read_sdist_text(path: Path, suffix: str) -> str | None:
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if member.name.endswith(suffix):
                extracted = archive.extractfile(member)
                if extracted is None:
                    return None
                return extracted.read().decode("utf-8")
    return None


def _metadata_version(text: str | None) -> str | None:
    if text is None:
        return None
    message = email.parser.Parser().parsestr(text)
    return message.get("Version")


def _version_from_filename(path: Path) -> str | None:
    if path.name.startswith("stui_terminal-") and path.name.endswith(".tar.gz"):
        return path.name.removeprefix("stui_terminal-").removesuffix(".tar.gz")
    match = re.match(r"^stui_terminal-([^-]+)(?:-|\\.tar\\.gz$)", path.name)
    if not match:
        return None
    return match.group(1)


def _check_wheel_metadata(
    path: Path,
    names: list[str],
    version: str | None,
) -> list[str]:
    errors: list[str] = []
    dist_info = _dist_info_prefix(names)
    if dist_info is None:
        errors.append(f"{path.name}: expected exactly one .dist-info directory")
        return errors

    metadata_name = f"{dist_info}/METADATA"
    entry_points_name = f"{dist_info}/entry_points.txt"
    if metadata_name in names:
        metadata_version = _metadata_version(_read_wheel_text(path, metadata_name))
        if version is not None and metadata_version != version:
            errors.append(
                f"{path.name}: METADATA version {metadata_version!r} != {version!r}"
            )
    if entry_points_name in names:
        entry_points = _read_wheel_text(path, entry_points_name)
        if ENTRY_POINT not in entry_points:
            errors.append(f"{path.name}: missing console entry point {ENTRY_POINT!r}")
    filename_version = _version_from_filename(path)
    if version is not None and filename_version != version:
        errors.append(
            f"{path.name}: filename version {filename_version!r} != {version!r}"
        )
    return errors


def _check_sdist_metadata(
    path: Path,
    names: list[str],
    version: str | None,
) -> list[str]:
    if version is None:
        return []

    errors: list[str] = []
    filename_version = _version_from_filename(path)
    if filename_version != version:
        errors.append(
            f"{path.name}: filename version {filename_version!r} != {version!r}"
        )
    root_parts = {Path(name).parts[0] for name in names if Path(name).parts}
    expected_root = f"stui_terminal-{version}"
    if root_parts != {expected_root}:
        errors.append(
            f"{path.name}: archive root {sorted(root_parts)!r} != {[expected_root]!r}"
        )
    pkg_info_version = _metadata_version(_read_sdist_text(path, "PKG-INFO"))
    if pkg_info_version != version:
        errors.append(
            f"{path.name}: PKG-INFO version {pkg_info_version!r} != {version!r}"
        )
    return errors


def _check_archive(
    path: Path,
    required_suffixes: set[str],
    *,
    version: str | None,
) -> list[str]:
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
        f"{path.name}: unsafe archive path {name}"
        for name in _unsafe_names(names)
    )
    errors.extend(
        f"{path.name}: forbidden package path {name}"
        for name in _forbidden_names(names)
    )
    if path.suffix == ".whl":
        errors.extend(_check_wheel_metadata(path, names, version))
    elif path.name.endswith(".tar.gz"):
        errors.extend(_check_sdist_metadata(path, names, version))
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
    parser.add_argument(
        "--version",
        help="Expected package version for filenames and metadata.",
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
        errors.extend(
            _check_archive(wheel[0], WHEEL_REQUIRED_SUFFIXES, version=args.version)
        )
    if sdist:
        errors.extend(
            _check_archive(sdist[0], SDIST_REQUIRED_SUFFIXES, version=args.version)
        )

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
