#!/usr/bin/env python3
"""Replay v2.2 cache and multi-file watch behavior outside the repository."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import pty
import re
import select
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import textwrap
import time
from pathlib import Path
from typing import Any

APP_SOURCE = """
from pathlib import Path

import stui as st

from data_loader import load_rows
from helpers import label


st.session_state.runs = st.session_state.get("runs", 0) + 1
st.session_state.cache_calls = st.session_state.get("cache_calls", 0)
st.session_state.row_calls = st.session_state.get("row_calls", 0)
st.session_state.resource_calls = st.session_state.get("resource_calls", 0)


@st.cache_data(ttl=60, max_entries=2)
def cached_label(name):
    st.session_state.cache_calls += 1
    return label(name)


@st.cache_data
def cached_rows(path):
    st.session_state.row_calls += 1
    return load_rows(path)


@st.cache_resource
def load_resource():
    st.session_state.resource_calls += 1
    return object()


clear_file = Path(".clear-caches")
if clear_file.exists():
    cached_label.clear()
    cached_rows.clear()
    load_resource.clear()
    clear_file.unlink()

cache_keys = st.session_state.get("cache_keys", ("alpha", "beta"))
labels = [cached_label(key) for key in cache_keys]
rows = cached_rows("sample_data.json")
rows[0]["score"] = -999
fresh_rows = cached_rows("sample_data.json")
first_resource = load_resource()
second_resource = load_resource()

st.title("External v2.2 workbench")
st.text(
    "proof "
    f"runs={st.session_state.runs} "
    f"cache_calls={st.session_state.cache_calls} "
    f"row_calls={st.session_state.row_calls} "
    f"resource_calls={st.session_state.resource_calls} "
    f"labels={','.join(labels)} "
    f"data_isolated={fresh_rows[0]['score'] == 0.9} "
    f"resource_same={first_resource is second_resource}"
)
with st.form("prompt-form"):
    st.text_area(
        "Prompt",
        "Summarize the local run.\\nKeep it concise.",
        key="prompt",
        max_chars=500,
    )
    st.multiselect("Signals", ["latency", "quality", "cost"], key="signals")
    st.toggle("Verbose diagnostics", key="verbose")
    st.form_submit_button("Apply")
st.table(fresh_rows)
st.bar_chart({"ready": 2, "failed": -1})
if not st.session_state.get("toast_sent", False):
    st.toast("external project ready")
    st.session_state.toast_sent = True
"""

HELPER_SOURCE = """
PREFIX = "v1"


def label(name):
    return f"{PREFIX}:{name}"
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
import importlib
import json
from pathlib import Path

from stui.app import StuiApp
from stui.elements import ErrorElement, TextElement
from stui.runtime import Runtime


ROOT = Path(__file__).resolve().parent
APP = ROOT / "app.py"
HELPER = ROOT / "helpers.py"


def proof_text(runtime):
    for element in runtime.elements:
        if isinstance(element, TextElement) and element.body.startswith("proof "):
            return element.body
    return ""


async def main():
    cache_module = importlib.import_module("stui.cache")
    clock = [0.0]
    cache_module._monotonic = lambda: clock[0]

    runtime = Runtime(APP)
    app = StuiApp(runtime, watch=True)
    notifications = []
    app.notify = lambda message, **kwargs: notifications.append(
        (message, kwargs.get("severity"))
    )
    app.set_interval = lambda *args, **kwargs: None

    async with app.run_test() as pilot:
        await pilot.pause()
        assert "runs=1" in proof_text(runtime)
        assert "cache_calls=2" in proof_text(runtime)
        assert "row_calls=1" in proof_text(runtime)
        assert "resource_calls=1" in proof_text(runtime)
        assert "data_isolated=True" in proof_text(runtime)
        assert "resource_same=True" in proof_text(runtime)

        await app.action_rerun_script()
        await pilot.pause()
        assert "runs=2" in proof_text(runtime)
        assert "cache_calls=2" in proof_text(runtime)

        runtime.session_state.cache_keys = ("gamma",)
        await app.action_rerun_script()
        await pilot.pause()
        assert runtime.session_state.cache_calls == 3

        runtime.session_state.cache_keys = ("alpha",)
        await app.action_rerun_script()
        await pilot.pause()
        assert runtime.session_state.cache_calls == 4

        clock[0] = 61.0
        runtime.session_state.cache_keys = ("gamma",)
        await app.action_rerun_script()
        await pilot.pause()
        assert runtime.session_state.cache_calls == 5

        (ROOT / ".clear-caches").write_text("clear", encoding="utf-8")
        await app.action_rerun_script()
        await pilot.pause()
        assert runtime.session_state.cache_calls == 6
        assert runtime.session_state.row_calls == 2
        assert runtime.session_state.resource_calls == 2

        (ROOT / "notes.txt").write_text("not watched", encoding="utf-8")
        await app._poll_script_change()
        await pilot.pause()
        reloads = [item for item in notifications if item[0].startswith("Reload")]
        assert reloads == []

        replacement = ROOT / ".helpers.py.tmp"
        replacement.write_text(
            "PREFIX = 'v2'\\n\\n"
            "def label(name):\\n"
            "    return f'{PREFIX}:{name}'\\n",
            encoding="utf-8",
        )
        replacement.replace(HELPER)
        await app._poll_script_change()
        await pilot.pause()
        assert "labels=v2:gamma" in proof_text(runtime)
        assert runtime.session_state.runs == 7
        assert runtime.session_state.cache_calls == 7
        assert runtime.session_state.row_calls == 3
        assert runtime.session_state.resource_calls == 3

        HELPER.write_text("PREFIX =\\n", encoding="utf-8")
        await app._poll_script_change()
        await pilot.pause()
        assert isinstance(runtime.elements[0], ErrorElement)
        assert runtime.session_state.runs == 7

        HELPER.write_text(
            "PREFIX = 'v3'\\n\\n"
            "def label(name):\\n"
            "    return f'{PREFIX}:{name}'\\n",
            encoding="utf-8",
        )
        await app._poll_script_change()
        await pilot.pause()
        assert "labels=v3:gamma" in proof_text(runtime)
        assert runtime.session_state.runs == 8

    reloads = [item for item in notifications if item[0].startswith("Reload")]
    assert reloads == [
        ("Reloaded helpers.py", "information"),
        ("Reload failed for helpers.py; watching continues", "error"),
        ("Reloaded helpers.py", "information"),
    ], reloads

    print(
        json.dumps(
            {
                "ok": True,
                "runs": runtime.session_state.runs,
                "cache_calls": runtime.session_state.cache_calls,
                "row_calls": runtime.session_state.row_calls,
                "resource_calls": runtime.session_state.resource_calls,
                "reload_notifications": reloads,
            },
            sort_keys=True,
        )
    )


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
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def _prepare_project(workdir: Path) -> None:
    if workdir.is_symlink() or not workdir.is_dir():
        raise RuntimeError(f"Work directory is not a real directory: {workdir}")
    if workdir.stat().st_mode & 0o077:
        raise RuntimeError(f"Work directory is not private (mode 0700): {workdir}")

    _write(workdir / "app.py", APP_SOURCE)
    _write(workdir / "helpers.py", HELPER_SOURCE)
    _write(workdir / "data_loader.py", DATA_LOADER_SOURCE)
    _write(workdir / "verify_project.py", HARNESS_SOURCE)
    (workdir / "sample_data.json").write_text(
        json.dumps(
            [
                {"name": "alpha", "score": 0.9},
                {"name": "beta", "score": 0.8},
            ]
        ),
        encoding="utf-8",
    )
    (workdir / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [project]
            name = "stui-v220-external-proof"
            version = "0.0.0"
            requires-python = ">=3.11"
            dependencies = ["stui-terminal"]
            """
        ).lstrip(),
        encoding="utf-8",
    )


def _python_for_project(workdir: Path, wheel: Path | None) -> Path:
    if wheel is None:
        # Keep the venv launcher path. Resolving its symlink would bypass the
        # environment and make installed metadata disagree with the import.
        return Path(sys.executable).absolute()
    venv = workdir / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv)],
        check=True,
    )
    python = venv / "bin" / "python"
    subprocess.run(
        [str(python), "-m", "pip", "install", str(wheel.resolve())],
        check=True,
    )
    return python


def _validate_json_result(
    result: subprocess.CompletedProcess[str],
    *,
    schema: str,
    require_ok: bool = True,
) -> dict[str, Any]:
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == schema, payload
    if require_ok:
        assert payload["ok"] is True, payload
    return payload


_ANSI_ESCAPE = re.compile(
    rb"(?:\x1B\[[0-?]*[ -/]*[@-~]|\x1B\][^\x07]*(?:\x07|\x1B\\))"
)


def _terminal_text(payload: bytes) -> str:
    return _ANSI_ESCAPE.sub(b"", payload).decode("utf-8", errors="replace")


def _run_cli_watch_proof(
    *,
    python: Path,
    workdir: Path,
    env: dict[str, str],
) -> dict[str, Any]:
    """Drive the installed ``stui run --watch`` command through a real PTY."""
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 34, 120, 0, 0))
    command = [str(python), "-m", "stui", "run", "app.py", "--watch"]
    process = subprocess.Popen(
        command,
        cwd=workdir,
        env={**env, "TERM": "xterm-256color"},
        stdin=slave,
        stdout=slave,
        stderr=slave,
        start_new_session=True,
        close_fds=True,
    )
    os.close(slave)
    output = bytearray()

    def wait_for(needle: str, timeout: float = 12.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if needle in _terminal_text(bytes(output)):
                return
            if process.poll() is not None:
                raise RuntimeError(
                    f"watch CLI exited before {needle!r}: "
                    f"{_terminal_text(bytes(output))[-2000:]}"
                )
            readable, _, _ = select.select([master], [], [], 0.2)
            if not readable:
                continue
            try:
                output.extend(os.read(master, 65536))
            except OSError:
                break
        raise TimeoutError(
            f"watch CLI did not render {needle!r}: "
            f"{_terminal_text(bytes(output))[-2000:]}"
        )

    helper = workdir / "helpers.py"
    try:
        wait_for("v3:alpha")
        helper.write_text(
            "PREFIX = 'v4'\n\ndef label(name):\n"
            "    return f'{PREFIX}:{name}'\n",
            encoding="utf-8",
        )
        wait_for("v4:alpha")

        helper.write_text("PREFIX =\n", encoding="utf-8")
        wait_for("SyntaxError")
        assert process.poll() is None

        helper.write_text(
            "PREFIX = 'v5'\n\ndef label(name):\n"
            "    return f'{PREFIX}:{name}'\n",
            encoding="utf-8",
        )
        wait_for("v5:alpha")
        assert process.poll() is None
        # The text area owns printable input while focused, so use SIGINT for
        # deterministic non-interactive shutdown instead of injecting "q".
        shutdown = "SIGINT"
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            shutdown = "SIGTERM fallback"
            process.terminate()
            process.wait(timeout=5)
        assert process.returncode in {0, -signal.SIGINT, -signal.SIGTERM}, (
            process.returncode
        )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        os.close(master)

    return {
        "ok": True,
        "command": command,
        "initial_helper": "v3",
        "reloaded_helper": "v4",
        "syntax_error_recovered": True,
        "fixed_helper": "v5",
        "shutdown": shutdown,
        "returncode": process.returncode,
    }


def _verify_project(workdir: Path, wheel: Path | None) -> int:
    _prepare_project(workdir)
    python = _python_for_project(workdir, wheel)
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    _run(
        [
            str(python),
            "-m",
            "py_compile",
            "app.py",
            "helpers.py",
            "data_loader.py",
            "verify_project.py",
        ],
        cwd=workdir,
        env=env,
    )
    doctor = _run(
        [str(python), "-m", "stui", "doctor", "--json"],
        cwd=workdir,
        env=env,
    )
    _validate_json_result(
        doctor,
        schema="stui.doctor.v1",
        require_ok=False,
    )
    checked = _run(
        [
            str(python),
            "-m",
            "stui",
            "check",
            "app.py",
            "--strict",
            "--repeat",
            "3",
            "--json",
        ],
        cwd=workdir,
        env=env,
    )
    check_payload = _validate_json_result(checked, schema="stui.check.v1")
    assert check_payload["summary"]["runs_completed"] == 3, check_payload

    watch_result = _run(
        [str(python), "verify_project.py"],
        cwd=workdir,
        env=env,
    )
    watch_payload = json.loads(watch_result.stdout)
    assert watch_payload["ok"] is True, watch_payload

    cli_watch_payload = _run_cli_watch_proof(
        python=python,
        workdir=workdir,
        env=env,
    )

    selftest = _run(
        [
            str(python),
            "-m",
            "stui",
            "selftest",
            "--strict",
            "--repeat",
            "2",
            "--json",
        ],
        cwd=workdir,
        env=env,
    )
    _validate_json_result(selftest, schema="stui.selftest.v1")

    proof = {
        "ok": True,
        "python": str(python),
        "wheel": str(wheel.resolve()) if wheel else None,
        "workdir": str(workdir),
        "check_runs": check_payload["summary"]["runs_completed"],
        "watch": watch_payload,
        "watch_cli": cli_watch_payload,
    }
    proof_path = workdir / "verification-result.json"
    proof_path.write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(proof, indent=2, sort_keys=True))
    print(f"v2.2 external project proof passed: {proof_path}")
    return 0


def _create_explicit_workdir(workdir: Path) -> Path:
    workdir = workdir.absolute()
    if workdir.is_symlink() or workdir.exists():
        raise RuntimeError(
            f"Refusing existing or symlinked work directory: {workdir}"
        )
    try:
        workdir.mkdir(mode=0o700)
    except FileExistsError as error:
        raise RuntimeError(
            f"Refusing existing or symlinked work directory: {workdir}"
        ) from error
    return workdir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()

    if args.workdir is not None:
        workdir = _create_explicit_workdir(args.workdir)
        return _verify_project(workdir, args.wheel)

    with tempfile.TemporaryDirectory(prefix="stui-v220-") as temporary:
        return _verify_project(Path(temporary), args.wheel)


if __name__ == "__main__":
    raise SystemExit(main())
