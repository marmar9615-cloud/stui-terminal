#!/usr/bin/env python3
"""Prove v2.3 workspace, diagnostics, and watch behavior outside the repo."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

APP_SOURCE = """
import stui as st

from data_loader import load_rows
from helpers import workspace_label


st.session_state.runs = st.session_state.get("runs", 0) + 1
st.session_state.data_calls = st.session_state.get("data_calls", 0)
st.session_state.resource_calls = st.session_state.get("resource_calls", 0)


@st.cache_data
def cached_rows(path):
    st.session_state.data_calls += 1
    return load_rows(path)


@st.cache_resource
def workspace_resource():
    st.session_state.resource_calls += 1
    return object()


rows = cached_rows("sample_data.json")
rows[0]["score"] = -1
fresh_rows = cached_rows("sample_data.json")
resource_a = workspace_resource()
resource_b = workspace_resource()

st.title("External v2.3 workspace")
st.text(
    "proof "
    f"label={workspace_label()} "
    f"runs={st.session_state.runs} "
    f"data_calls={st.session_state.data_calls} "
    f"resource_calls={st.session_state.resource_calls} "
    f"isolated={fresh_rows[0]['score'] == 91} "
    f"resource_same={resource_a is resource_b}"
)

overview, data, files = st.tabs(
    ["Overview", "Data", "Files"],
    key="workspace-tabs",
)
with overview:
    st.text_area("Notes", "Inspect the local run.", key="notes")
    st.multiselect("Signals", ["quality", "latency"], key="signals")
    st.toggle("Verbose", key="verbose")
with data:
    selected = st.data_table(
        fresh_rows,
        selection_mode="single",
        key="selected-row",
        show_index=True,
    )
    st.caption(f"selected={selected}")
with files:
    st.path_input(
        "Data file",
        "sample_data.json",
        kind="file",
        must_exist=True,
        extensions=["json"],
        key="data-path",
    )

if not st.session_state.get("toast_sent", False):
    st.toast("workspace ready")
    st.session_state.toast_sent = True
"""

HELPER_SOURCE = """
LABEL = "workspace-v1"


def workspace_label():
    return LABEL
"""

DATA_LOADER_SOURCE = """
import json
from pathlib import Path


def load_rows(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
"""

HARNESS_SOURCE = """
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from textual.widgets import Tabs

from stui.app import StuiApp
from stui.elements import ErrorElement, TextElement
from stui.runtime import Runtime
from stui.widgets.data_table import StuiDataTable


ROOT = Path(__file__).resolve().parent
APP = ROOT / "app.py"
HELPER = ROOT / "helpers.py"


def proof_text(runtime):
    for element in runtime.elements:
        if isinstance(element, TextElement) and element.body.startswith("proof "):
            return element.body
    return ""


async def main():
    runtime = Runtime(APP)
    app = StuiApp(runtime, watch=True)
    app.set_interval = lambda *args, **kwargs: None
    notifications = []
    app.notify = lambda message, **kwargs: notifications.append(message)

    async with app.run_test(headless=True, size=(100, 32)) as pilot:
        await pilot.pause()
        assert not any(isinstance(item, ErrorElement) for item in runtime.elements)
        assert "label=workspace-v1" in proof_text(runtime)
        assert "data_calls=1" in proof_text(runtime)
        assert "resource_calls=1" in proof_text(runtime)
        assert "isolated=True" in proof_text(runtime)
        assert "resource_same=True" in proof_text(runtime)

        await app.action_rerun_script()
        await pilot.pause()
        assert "runs=2" in proof_text(runtime)
        assert "data_calls=1" in proof_text(runtime)
        assert "resource_calls=1" in proof_text(runtime)

        tabs = app.query_one(Tabs)
        app.set_focus(tabs)
        await pilot.press("right")
        await pilot.pause()
        assert runtime.session_state["workspace-tabs"] == 1

        table = app.query_one(StuiDataTable)
        app.set_focus(table)
        await pilot.press("enter")
        await pilot.pause()
        assert runtime.session_state["selected-row"] == 0

        commands = {
            command.title for command in app.get_system_commands(app.screen)
        }
        assert "Rerun app" in commands
        assert "Diagnostics" in commands
        assert "Switch tab: Files" in commands

        HELPER.write_text(
            "LABEL = 'workspace-v2'\\n\\n"
            "def workspace_label():\\n"
            "    return LABEL\\n",
            encoding="utf-8",
        )
        await app._poll_script_change()
        await pilot.pause()
        assert "label=workspace-v2" in proof_text(runtime)
        assert runtime.session_state["selected-row"] == 0
        # Initial render + manual rerun + tab change + row selection + watch reload.
        assert runtime.session_state.runs == 5

    print(json.dumps({
        "ok": True,
        "runs": runtime.session_state.runs,
        "data_calls": runtime.session_state.data_calls,
        "resource_calls": runtime.session_state.resource_calls,
        "selected_row": runtime.session_state["selected-row"],
        "watch_reloaded": any("Reloaded helpers.py" in item for item in notifications),
    }, sort_keys=True))


asyncio.run(main())
"""


def _write(path: Path, value: str) -> None:
    path.write_text(textwrap.dedent(value).lstrip(), encoding="utf-8")


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def _json_result(
    result: subprocess.CompletedProcess[str],
    schema: str,
) -> dict[str, Any]:
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == schema, payload
    assert payload["ok"] is True, payload
    return payload


def _venv_python(root: Path) -> Path:
    scripts = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return root / scripts / executable


def _prepare_project(root: Path) -> None:
    _write(root / "app.py", APP_SOURCE)
    _write(root / "helpers.py", HELPER_SOURCE)
    _write(root / "data_loader.py", DATA_LOADER_SOURCE)
    _write(root / "verify_workspace.py", HARNESS_SOURCE)
    (root / "sample_data.json").write_text(
        json.dumps(
            [
                {"name": "alpha", "score": 91},
                {"name": "beta", "score": 87},
            ]
        ),
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        "[project]\nname='stui-v230-proof'\nversion='0.0.0'\n"
        "requires-python='>=3.11'\ndependencies=['stui-terminal']\n",
        encoding="utf-8",
    )


def verify(root: Path, wheel: Path) -> dict[str, object]:
    if root.is_symlink() or not root.is_dir() or root.stat().st_mode & 0o077:
        raise RuntimeError("verification root must be a private real directory")
    _prepare_project(root)
    environment = root / ".venv"
    subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
    python = _venv_python(environment)
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-cache-dir", str(wheel)],
        check=True,
    )
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    _run(
        [str(python), "-m", "py_compile", "app.py", "helpers.py", "data_loader.py"],
        cwd=root,
        env=env,
    )
    checked = _json_result(
        _run(
            [
                str(python), "-m", "stui", "check", "app.py",
                "--strict", "--repeat", "3", "--json",
            ],
            cwd=root,
            env=env,
        ),
        "stui.check.v1",
    )
    inspected = _json_result(
        _run(
            [
                str(python), "-m", "stui", "inspect", "app.py",
                "--strict", "--repeat", "3", "--json",
            ],
            cwd=root,
            env=env,
        ),
        "stui.inspect.v1",
    )
    harness = json.loads(
        _run([str(python), "verify_workspace.py"], cwd=root, env=env).stdout
    )
    assert harness["ok"] is True, harness
    assert harness["watch_reloaded"] is True, harness
    assert harness["runs"] == 5, harness

    demo_list = _run(
        [str(python), "-m", "stui", "demo", "list"], cwd=root, env=env
    ).stdout
    assert all(name in demo_list for name in ("workspace", "tabs", "data_explorer"))
    generated = root / "generated.py"
    _run(
        [
            str(python), "-m", "stui", "init", str(generated),
            "--template", "workspace",
        ],
        cwd=root,
        env=env,
    )
    _json_result(
        _run(
            [
                str(python), "-m", "stui", "check", str(generated),
                "--strict", "--json",
            ],
            cwd=root,
            env=env,
        ),
        "stui.check.v1",
    )
    _json_result(
        _run(
            [
                str(python), "-m", "stui", "selftest",
                "--strict", "--repeat", "2", "--json",
            ],
            cwd=root,
            env=env,
        ),
        "stui.selftest.v1",
    )

    proof = {
        "schema_version": "stui.v230-project-proof.v1",
        "ok": True,
        "wheel": wheel.name,
        "check_runs": checked["summary"]["runs_completed"],
        "inspect_runs": inspected["summary"]["runs_completed"],
        "harness": harness,
    }
    (root / "verification-result.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return proof


def _exclusive_workdir(path: Path) -> Path:
    path = path.absolute()
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"refusing existing verification directory: {path}")
    path.mkdir(mode=0o700)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--workdir", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve()
    if not wheel.is_file():
        raise RuntimeError(f"wheel not found: {wheel}")

    if args.workdir is not None:
        root = _exclusive_workdir(args.workdir)
        print(json.dumps(verify(root, wheel), indent=2, sort_keys=True))
        return 0

    with tempfile.TemporaryDirectory(prefix="stui-v230-") as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        print(json.dumps(verify(root, wheel), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
