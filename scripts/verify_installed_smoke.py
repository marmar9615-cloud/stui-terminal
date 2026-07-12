from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _wheel_from_dist(dist: Path) -> Path:
    wheels = sorted(dist.glob("stui_terminal-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(
            f"expected exactly one stui wheel in {dist}, found {len(wheels)}"
        )
    return wheels[0].resolve()


def _venv_python(environment: Path) -> Path:
    scripts = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return environment / scripts / executable


def _run(python: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(python), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _create_venv(environment: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "venv", str(environment)],
        check=True,
    )


def _json_command(python: Path, *args: str) -> dict[str, object]:
    result = _run(python, "-m", "stui", *args)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object from {' '.join(args)}")
    return payload


def verify(dist: Path) -> dict[str, object]:
    wheel = _wheel_from_dist(dist)
    with tempfile.TemporaryDirectory(prefix="stui-installed-smoke-") as tmp:
        root = Path(tmp)
        environment = root / "venv"
        _create_venv(environment)
        python = _venv_python(environment)

        _run(python, "-m", "pip", "install", "--no-cache-dir", str(wheel))
        version = _run(
            python,
            "-c",
            "import stui; print(stui.__version__)",
        ).stdout.strip()
        module_version = _run(python, "-m", "stui", "--version").stdout.strip()
        doctor = _json_command(python, "doctor", "--json")
        selftest = _json_command(
            python,
            "selftest",
            "--strict",
            "--repeat",
            "2",
            "--json",
        )
        demos = _run(python, "-m", "stui", "demo", "list").stdout
        examples = _run(python, "-m", "stui", "example", "list").stdout

        app_path = root / "app.py"
        _run(python, "-m", "stui", "init", str(app_path))
        checked = _json_command(
            python,
            "check",
            str(app_path),
            "--strict",
            "--repeat",
            "2",
            "--json",
        )

        if doctor.get("stui") != version:
            raise RuntimeError("doctor version does not match imported version")
        if selftest.get("ok") is not True:
            raise RuntimeError("strict installed-package selftest failed")
        if checked.get("ok") is not True:
            raise RuntimeError("generated app validation failed")
        if "basic" not in demos or "basic" not in examples:
            raise RuntimeError("bundled basic demo/example was not discoverable")

        return {
            "schema_version": "stui.installed-smoke.v1",
            "ok": True,
            "wheel": wheel.name,
            "version": version,
            "module_version": module_version,
            "doctor_schema": doctor.get("schema_version"),
            "selftest_schema": selftest.get("schema_version"),
            "check_schema": checked.get("schema_version"),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a built stui wheel in a clean cross-platform venv."
    )
    parser.add_argument(
        "dist",
        nargs="?",
        default="dist",
        type=Path,
        help="Directory containing exactly one stui wheel.",
    )
    args = parser.parse_args()
    result = verify(args.dist.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
