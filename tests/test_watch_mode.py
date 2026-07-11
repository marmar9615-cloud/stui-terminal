from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from stui.app import StuiApp
from stui.elements import ErrorElement, TextElement
from stui.runtime import Runtime

MODULE_NAMES = ("watch_helper", "watch_package", "watch_package.nested")


@pytest.fixture(autouse=True)
def clean_watch_modules() -> None:
    for name in MODULE_NAMES:
        sys.modules.pop(name, None)
    yield
    for name in MODULE_NAMES:
        sys.modules.pop(name, None)


def _text(elements: list[object]) -> list[str]:
    return [element.body for element in elements if isinstance(element, TextElement)]


def _write_app(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def _disable_automatic_watch_poll(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep app-level watch tests deterministic while polling explicitly."""
    monkeypatch.setattr(StuiApp, "set_interval", lambda *args, **kwargs: None)


def _notification_recorder(
    notifications: list[tuple[str, str | None]],
):
    def record(message: str, **kwargs: Any) -> None:
        notifications.append((message, kwargs.get("severity")))

    return record


def test_watch_tracks_and_reloads_imported_local_module(tmp_path: Path) -> None:
    helper = tmp_path / "watch_helper.py"
    app = tmp_path / "app.py"
    helper.write_text('VALUE = "first"\n', encoding="utf-8")
    _write_app(
        app,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    runtime = Runtime(app)

    assert _text(runtime.run_script()) == ["first"]
    assert runtime.watched_source_paths == (app.resolve(), helper.resolve())
    assert runtime.poll_source_changes() == ()

    original_stat = helper.stat()
    helper.write_text('VALUE = "other"\n', encoding="utf-8")
    os.utime(helper, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

    changed = runtime.poll_source_changes()
    assert changed == (helper.resolve(),)
    evicted = runtime.prepare_source_reload(changed)

    assert evicted == ("watch_helper",)
    assert _text(runtime.run_script()) == ["other"]


def test_watch_detects_atomic_app_replace_and_ignores_unrelated_files(
    tmp_path: Path,
) -> None:
    app = tmp_path / "app.py"
    _write_app(app, "import stui as st\nst.text('before')\n")
    runtime = Runtime(app)

    assert _text(runtime.run_script()) == ["before"]
    (tmp_path / "notes.txt").write_text("unrelated", encoding="utf-8")
    assert runtime.poll_source_changes() == ()

    replacement = tmp_path / ".app.py.tmp"
    _write_app(replacement, "import stui as st\nst.text('after')\n")
    replacement.replace(app)

    changed = runtime.poll_source_changes()
    assert changed == (app.resolve(),)
    assert runtime.poll_source_changes() == ()
    runtime.prepare_source_reload(changed)
    assert _text(runtime.run_script()) == ["after"]


def test_watch_reloads_nested_modules_but_keeps_third_party_modules(
    tmp_path: Path,
) -> None:
    package = tmp_path / "watch_package"
    package.mkdir()
    (package / "__init__.py").write_text(
        "from .nested import value\n", encoding="utf-8"
    )
    nested = package / "nested.py"
    nested.write_text('value = "before"\n', encoding="utf-8")
    app = tmp_path / "app.py"
    _write_app(
        app,
        "import json\n"
        "import stui as st\n"
        "from watch_package import value\n"
        "st.text(value)\n",
    )
    runtime = Runtime(app)

    assert _text(runtime.run_script()) == ["before"]
    json_module = sys.modules[json.__name__]
    nested.write_text('value = "after"\n', encoding="utf-8")

    changed = runtime.poll_source_changes()
    evicted = runtime.prepare_source_reload(changed)

    assert set(evicted) == {"watch_package", "watch_package.nested"}
    assert sys.modules[json.__name__] is json_module
    assert _text(runtime.run_script()) == ["after"]


def test_watch_syntax_error_recovers_and_preserves_session_state(
    tmp_path: Path,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "ready"\n', encoding="utf-8")
    app = tmp_path / "app.py"
    _write_app(
        app,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        'st.session_state.count = st.session_state.get("count", 0) + 1\n'
        'st.text(f"{VALUE}:{st.session_state.count}")\n',
    )
    runtime = Runtime(app)

    assert _text(runtime.run_script()) == ["ready:1"]
    helper.write_text("VALUE =\n", encoding="utf-8")
    runtime.prepare_source_reload(runtime.poll_source_changes())

    broken = runtime.run_script()
    assert isinstance(broken[0], ErrorElement)
    assert "SyntaxError" in broken[0].traceback
    assert runtime.session_state.count == 1

    helper.write_text('VALUE = "fixed"\n', encoding="utf-8")
    runtime.prepare_source_reload(runtime.poll_source_changes())

    assert _text(runtime.run_script()) == ["fixed:2"]


def test_watch_deleted_helper_can_be_recreated(tmp_path: Path) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "ready"\n', encoding="utf-8")
    app = tmp_path / "app.py"
    _write_app(
        app,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    runtime = Runtime(app)

    assert _text(runtime.run_script()) == ["ready"]
    helper.unlink()
    assert runtime.poll_source_changes() == (helper.resolve(),)
    runtime.prepare_source_reload((helper,))
    missing = runtime.run_script()
    assert isinstance(missing[0], ErrorElement)

    helper.write_text('VALUE = "restored"\n', encoding="utf-8")
    assert runtime.poll_source_changes() == (helper.resolve(),)
    runtime.prepare_source_reload((helper,))
    assert _text(runtime.run_script()) == ["restored"]


def test_watch_coalesces_rapid_changes_and_notifies_cache_hook(
    tmp_path: Path,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "zero"\n', encoding="utf-8")
    app = tmp_path / "app.py"
    _write_app(
        app,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    runtime = Runtime(app)
    runtime.run_script()
    notifications: list[tuple[frozenset[Path], int]] = []
    runtime.add_source_change_callback(
        lambda paths, revision: notifications.append((paths, revision))
    )

    helper.write_text('VALUE = "one"\n', encoding="utf-8")
    helper.write_text('VALUE = "two"\n', encoding="utf-8")
    helper.write_text('VALUE = "done"\n', encoding="utf-8")

    changed = runtime.poll_source_changes()
    runtime.prepare_source_reload(changed)

    assert changed == (helper.resolve(),)
    assert runtime.source_revision == 1
    assert notifications == [(frozenset({helper.resolve()}), 1)]
    assert _text(runtime.run_script()) == ["done"]


def test_watch_ignores_known_generated_and_environment_trees(tmp_path: Path) -> None:
    app = tmp_path / "app.py"
    _write_app(app, "import stui as st\nst.text('ok')\n")
    runtime = Runtime(app)

    ignored = [
        tmp_path / ".venv" / "lib" / "helper.py",
        tmp_path / ".venv.nosync" / "lib" / "helper.py",
        tmp_path / ".git" / "helper.py",
        tmp_path / "__pycache__" / "helper.py",
        tmp_path / "build" / "helper.py",
        tmp_path / "dist" / "helper.py",
    ]

    assert all(not runtime.is_watchable_source(path) for path in ignored)
    assert runtime.is_watchable_source(tmp_path / "src" / "helper.py")


def test_stui_app_watch_reloads_helper_and_reports_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "before"\n', encoding="utf-8")
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert _text(runtime.elements) == ["before"]

            helper.write_text('VALUE = "after"\n', encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["after"]
            assert notifications == [
                ("Reloaded watch_helper.py", "information"),
            ]

    asyncio.run(scenario())


def test_stui_app_watch_failure_and_recovery_notifications_are_accurate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "ready"\n', encoding="utf-8")
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        'st.session_state.runs = st.session_state.get("runs", 0) + 1\n'
        'st.text(f"{VALUE}:{st.session_state.runs}")\n',
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert _text(runtime.elements) == ["ready:1"]

            helper.write_text("VALUE =\n", encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()

            assert isinstance(runtime.elements[0], ErrorElement)
            assert runtime.session_state.runs == 1
            assert notifications == [
                (
                    "Reload failed for watch_helper.py; watching continues",
                    "error",
                ),
            ]
            assert not any(
                message.startswith("Reloaded")
                for message, _ in notifications
            )

            helper.write_text('VALUE = "fixed"\n', encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["fixed:2"]
            assert runtime.session_state.runs == 2
            assert notifications == [
                (
                    "Reload failed for watch_helper.py; watching continues",
                    "error",
                ),
                ("Reloaded watch_helper.py", "information"),
            ]

    asyncio.run(scenario())


def test_stui_app_watch_app_syntax_error_reports_failure_then_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        'st.session_state.runs = st.session_state.get("runs", 0) + 1\n'
        'st.text(f"ready:{st.session_state.runs}")\n',
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert _text(runtime.elements) == ["ready:1"]

            _write_app(app_path, "import stui as st\nst.title(\n")
            await app._poll_script_change()
            await pilot.pause()

            assert isinstance(runtime.elements[0], ErrorElement)
            assert runtime.session_state.runs == 1
            assert notifications == [
                (
                    "Reload failed for app.py; watching continues",
                    "error",
                ),
            ]

            _write_app(
                app_path,
                "import stui as st\n"
                'st.session_state.runs = st.session_state.get("runs", 0) + 1\n'
                'st.text(f"fixed:{st.session_state.runs}")\n',
            )
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["fixed:2"]
            assert notifications[-1] == (
                "Reloaded app.py",
                "information",
            )

    asyncio.run(scenario())


def test_stui_app_watch_coalesces_atomic_and_rapid_helper_saves(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "zero"\n', encoding="utf-8")
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()

            first = tmp_path / ".watch_helper.py.first.tmp"
            first.write_text('VALUE = "one"\n', encoding="utf-8")
            first.replace(helper)
            second = tmp_path / ".watch_helper.py.second.tmp"
            second.write_text('VALUE = "final"\n', encoding="utf-8")
            second.replace(helper)

            await app._poll_script_change()
            await pilot.pause()
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["final"]
            assert notifications == [
                ("Reloaded watch_helper.py", "information"),
            ]

    asyncio.run(scenario())


def test_stui_app_watch_ignores_untracked_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_path = tmp_path / "app.py"
    _write_app(app_path, "import stui as st\nst.text('steady')\n")
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["steady"]
            assert notifications == []

    asyncio.run(scenario())


def test_stui_app_watch_helper_delete_and_recreate_recovers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "ready"\n', encoding="utf-8")
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        "st.text(VALUE)\n",
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            helper.unlink()
            await app._poll_script_change()
            await pilot.pause()
            assert isinstance(runtime.elements[0], ErrorElement)
            assert notifications == [
                (
                    "Reload failed for watch_helper.py; watching continues",
                    "error",
                ),
            ]

            helper.write_text('VALUE = "restored"\n', encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()
            assert _text(runtime.elements) == ["restored"]
            assert notifications[-1] == (
                "Reloaded watch_helper.py",
                "information",
            )

    asyncio.run(scenario())


def test_stui_app_watch_invalidates_helper_dependent_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text('VALUE = "first"\n', encoding="utf-8")
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import VALUE\n"
        'st.session_state.calls = st.session_state.get("calls", 0)\n'
        "@st.cache_data\n"
        "def cached_value():\n"
        "    st.session_state.calls += 1\n"
        "    return VALUE\n"
        'st.text(f"{cached_value()}:{st.session_state.calls}")\n',
    )
    _disable_automatic_watch_poll(monkeypatch)

    async def scenario() -> None:
        runtime = Runtime(app_path)
        app = StuiApp(runtime, watch=True)
        notifications: list[tuple[str, str | None]] = []
        app.notify = _notification_recorder(notifications)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert _text(runtime.elements) == ["first:1"]

            await app.action_rerun_script()
            await pilot.pause()
            assert _text(runtime.elements) == ["first:1"]

            helper.write_text('VALUE = "fresh"\n', encoding="utf-8")
            await app._poll_script_change()
            await pilot.pause()

            assert _text(runtime.elements) == ["fresh:2"]
            assert notifications == [
                ("Reloaded watch_helper.py", "information"),
            ]

    asyncio.run(scenario())


def test_watch_helper_runtime_error_reports_local_helper_frame(
    tmp_path: Path,
) -> None:
    helper = tmp_path / "watch_helper.py"
    helper.write_text(
        "def render():\n"
        "    return 'ready'\n",
        encoding="utf-8",
    )
    app_path = tmp_path / "app.py"
    _write_app(
        app_path,
        "import stui as st\n"
        "from watch_helper import render\n"
        "st.text(render())\n",
    )
    runtime = Runtime(app_path)

    assert _text(runtime.run_script()) == ["ready"]
    helper.write_text(
        "def render():\n"
        "    raise RuntimeError('helper exploded')\n",
        encoding="utf-8",
    )
    changed = runtime.poll_source_changes()
    runtime.prepare_source_reload(changed)

    elements = runtime.run_script()
    assert isinstance(elements[0], ErrorElement)
    assert str(helper.resolve()) in elements[0].traceback
    assert "raise RuntimeError('helper exploded')" in elements[0].traceback
