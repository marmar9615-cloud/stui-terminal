from __future__ import annotations

import importlib.util
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_v220_project.py"
SPEC = importlib.util.spec_from_file_location("verify_v220_project", SCRIPT)
assert SPEC is not None
verify_v220_project = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify_v220_project)


def test_default_workdir_is_private_unique_and_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    class StopAfterInspection(Exception):
        pass

    def inspect_workdir(workdir: Path) -> None:
        observed["path"] = workdir
        observed["exists"] = workdir.is_dir()
        observed["mode"] = stat.S_IMODE(workdir.stat().st_mode)
        raise StopAfterInspection

    monkeypatch.setattr(verify_v220_project, "_prepare_project", inspect_workdir)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT)])

    with pytest.raises(StopAfterInspection):
        verify_v220_project.main()

    workdir = observed["path"]
    assert isinstance(workdir, Path)
    assert workdir.name.startswith("stui-v220-")
    assert workdir != Path("/tmp/stui-v220-workbench")
    assert observed["exists"] is True
    assert observed["mode"] == 0o700
    assert not workdir.exists()
