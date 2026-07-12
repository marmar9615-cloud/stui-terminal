from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.verify_installed_smoke import _create_venv, _wheel_from_dist


def test_create_venv_uses_platform_native_module_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run(command: list[str], *, check: bool):
        calls.append((command, check))

    monkeypatch.setattr(subprocess, "run", fake_run)
    environment = tmp_path / "venv"

    _create_venv(environment)

    assert calls == [
        ([sys.executable, "-m", "venv", str(environment)], True)
    ]


def test_wheel_from_dist_requires_exactly_one_wheel(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="expected exactly one"):
        _wheel_from_dist(tmp_path)

    wheel = tmp_path / "stui_terminal-2.3.0-py3-none-any.whl"
    wheel.touch()
    assert _wheel_from_dist(tmp_path) == wheel.resolve()

    (tmp_path / "stui_terminal-2.3.1-py3-none-any.whl").touch()
    with pytest.raises(RuntimeError, match="found 2"):
        _wheel_from_dist(tmp_path)
