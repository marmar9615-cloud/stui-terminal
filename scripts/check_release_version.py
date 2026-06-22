from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _package_version() -> str:
    text = (ROOT / "src/stui/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', text, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError("could not find src/stui/__init__.py __version__")
    return match.group(1)


def _expected_tag(version: str) -> str:
    return f"v{version}"


def check_release_version(tag: str | None = None) -> list[str]:
    project_version = _project_version()
    package_version = _package_version()
    errors: list[str] = []

    if project_version != package_version:
        errors.append(
            "pyproject.toml project.version "
            f"({project_version}) does not match stui.__version__ "
            f"({package_version})"
        )

    if tag and tag.startswith("v") and tag != _expected_tag(project_version):
        errors.append(
            f"git tag {tag} does not match project version {project_version}; "
            f"expected {_expected_tag(project_version)}"
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify release version metadata before publishing."
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Optional Git tag or ref name to compare with project.version.",
    )
    args = parser.parse_args(argv)

    errors = check_release_version(args.tag)
    if errors:
        for error in errors:
            print(f"release version check failed: {error}", file=sys.stderr)
        return 1

    print(f"release version ok: {_project_version()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
