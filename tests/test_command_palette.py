import asyncio
import inspect
from pathlib import Path

from textual.color import Color

from stui.app import StuiApp
from stui.cache import cache_info
from stui.runtime import Runtime


async def _invoke(command) -> None:
    result = command.callback()
    if inspect.isawaitable(result):
        await result


def test_command_palette_exposes_only_safe_builtin_actions(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("import stui as st\nst.write('ready')\n", encoding="utf-8")

    async def scenario() -> None:
        app = StuiApp(Runtime(script))
        async with app.run_test() as pilot:
            await pilot.pause()
            commands = list(app.get_system_commands(app.screen))

            assert [command.title for command in commands] == [
                "Rerun app",
                "Quit",
                "Toggle theme",
                "Clear data cache",
                "Clear resource cache",
                "Focus next widget",
                "Diagnostics",
                "Help",
            ]
            assert "Screenshot" not in {command.title for command in commands}
            assert "Theme" not in {command.title for command in commands}
            assert not hasattr(StuiApp, "register_command")
            assert all(
                word not in command.title.lower()
                for command in commands
                for word in ("shell", "python", "eval", "exec")
            )

    asyncio.run(scenario())


def test_command_palette_actions_use_runtime_scoped_state(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

st.session_state.runs = st.session_state.get("runs", 0) + 1

@st.cache_data
def load_data():
    return "data-secret"

@st.cache_resource
def load_resource():
    return "resource-secret"

st.text_input("Name", key="name")
st.write(load_data(), load_resource())
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)
        async with app.run_test() as pilot:
            await pilot.pause()
            commands = {
                command.title: command
                for command in app.get_system_commands(app.screen)
            }
            assert runtime.session_state.runs == 1
            assert cache_info(runtime)["data"]["entries"] == 1
            assert cache_info(runtime)["resource"]["entries"] == 1

            await _invoke(commands["Rerun app"])
            await pilot.pause()
            assert runtime.session_state.runs == 2
            assert cache_info(runtime)["data"]["entries"] == 1
            assert cache_info(runtime)["resource"]["entries"] == 1

            await _invoke(commands["Clear data cache"])
            assert cache_info(runtime)["data"]["entries"] == 0
            assert cache_info(runtime)["resource"]["entries"] == 1

            await _invoke(commands["Clear resource cache"])
            assert cache_info(runtime)["resource"]["entries"] == 0

            app.set_focus(None)
            await _invoke(commands["Focus next widget"])
            await pilot.pause()
            assert getattr(app.focused, "stui_key", None) == "name"

            original_theme = app.stui_theme
            original_textual_theme = app.theme
            original_background = app.screen.styles.background
            await _invoke(commands["Toggle theme"])
            await pilot.pause()
            assert app.stui_theme != original_theme
            assert app.theme == original_textual_theme
            assert app.screen.styles.background != original_background
            await _invoke(commands["Toggle theme"])
            await pilot.pause()
            assert app.stui_theme == original_theme
            assert app.screen.styles.background == original_background

    asyncio.run(scenario())


def test_palette_diagnostics_are_count_only(tmp_path: Path, monkeypatch) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

st.session_state["state-secret-key"] = "state-secret-value"
st.text_input("rendered-secret", value="widget-secret", key="input-secret")
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)
    runtime.run_script()
    app = StuiApp(runtime)
    notifications: list[str] = []

    def capture(message: str, **_kwargs) -> None:
        notifications.append(message)

    monkeypatch.setattr(app, "notify", capture)

    app.action_show_diagnostics()

    assert len(notifications) == 1
    assert "elements=1" in notifications[0]
    assert "widgets=1" in notifications[0]
    assert "session_keys=2" in notifications[0]
    assert "watch_files=1" in notifications[0]
    assert "cache_entries=0" in notifications[0]
    for secret in (
        "state-secret-key",
        "state-secret-value",
        "rendered-secret",
        "widget-secret",
        "input-secret",
    ):
        assert secret not in notifications[0]


def test_theme_toggle_applies_high_contrast_to_command_palette(
    tmp_path: Path,
) -> None:
    script = tmp_path / "app.py"
    script.write_text("import stui as st\nst.write('ready')\n", encoding="utf-8")

    async def scenario() -> None:
        app = StuiApp(Runtime(script))
        async with app.run_test() as pilot:
            await pilot.pause()
            app.action_toggle_theme()
            await pilot.pause()
            assert app.stui_theme == "high-contrast"

            await pilot.press("ctrl+p")
            await pilot.pause()
            assert type(app.screen).__name__ == "CommandPalette"
            assert app.screen.styles.background == Color.parse("#000000")

    asyncio.run(scenario())


def test_switch_tab_commands_are_available_only_through_specific_hook(
    tmp_path: Path,
) -> None:
    script = tmp_path / "app.py"
    script.write_text("import stui as st\nst.write('ready')\n", encoding="utf-8")
    switched: list[tuple[str, int]] = []

    class TabIntegratedApp(StuiApp):
        def _command_palette_tab_targets(self):
            return (
                ("workspace", 0, "Overview"),
                ("workspace", 1, "Details"),
            )

        async def _switch_command_palette_tab(self, key: str, index: int) -> None:
            switched.append((key, index))

    app = TabIntegratedApp(Runtime(script))
    commands = {command.title: command for command in app.get_system_commands(None)}

    assert "Switch tab: Overview" in commands
    assert "Switch tab: Details" in commands
    asyncio.run(_invoke(commands["Switch tab: Details"]))
    assert switched == [("workspace", 1)]
