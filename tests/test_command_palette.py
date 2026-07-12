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


def test_command_palette_discovers_and_switches_runtime_tabs(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

overview, details = st.tabs(["Overview", "Details"], key="workspace")
with overview:
    st.write("overview")
with details:
    st.write("details")
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

            assert "Switch tab: Overview" in commands
            assert "Switch tab: Details" in commands
            assert runtime.session_state["workspace"] == 0

            await _invoke(commands["Switch tab: Details"])
            await pilot.pause()

            assert runtime.session_state["workspace"] == 1

    asyncio.run(scenario())


def test_command_palette_neutralizes_tab_label_controls(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

safe, danger = st.tabs(["Safe", "Danger\\nQuit\\tNow"], key="workspace")
with safe:
    st.write("safe")
with danger:
    st.write("danger")
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)
    runtime.run_script()

    titles = [
        command.title
        for command in StuiApp(runtime).get_system_commands(None)
    ]

    assert "Switch tab: Danger\\nQuit\\tNow" in titles
    assert all("\n" not in title and "\t" not in title for title in titles)


def test_command_palette_disambiguates_duplicate_tab_labels(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

first_a, first_b = st.tabs(["Overview", "Details"], key="first")
with first_a:
    st.write("first overview")
with first_b:
    st.write("first details")

second_a, second_b = st.tabs(["Overview", "Details"], key="second")
with second_a:
    st.write("second overview")
with second_b:
    st.write("second details")
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)
    runtime.run_script()

    titles = [
        command.title
        for command in StuiApp(runtime).get_system_commands(None)
        if command.title.startswith("Switch tab:")
    ]

    assert titles == [
        "Switch tab: Overview [first]",
        "Switch tab: Details [first]",
        "Switch tab: Overview [second]",
        "Switch tab: Details [second]",
    ]


def test_command_palette_omits_tabs_nested_in_inactive_panes(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

visible, hidden = st.tabs(["Visible", "Hidden"], key="outer")
with visible:
    visible_a, visible_b = st.tabs(["Visible A", "Visible B"], key="visible")
    with visible_a:
        st.write("visible a")
    with visible_b:
        st.write("visible b")
with hidden:
    hidden_a, hidden_b = st.tabs(["Hidden A", "Hidden B"], key="hidden")
    with hidden_a:
        st.write("hidden a")
    with hidden_b:
        st.write("hidden b")
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)
    runtime.run_script()

    titles = {
        command.title
        for command in StuiApp(runtime).get_system_commands(None)
    }

    assert {"Switch tab: Visible", "Switch tab: Hidden"} <= titles
    assert {"Switch tab: Visible A", "Switch tab: Visible B"} <= titles
    assert "Switch tab: Hidden A" not in titles
    assert "Switch tab: Hidden B" not in titles


def test_command_palette_omits_tabs_in_collapsed_groups(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st

with st.expander("Collapsed expander", expanded=False):
    expander_a, expander_b = st.tabs(
        ["Hidden expander A", "Hidden expander B"],
        key="hidden-expander-tabs",
    )
    with expander_a:
        st.write("hidden expander a")
    with expander_b:
        st.write("hidden expander b")

with st.status("Collapsed status", expanded=False):
    status_a, status_b = st.tabs(
        ["Hidden status A", "Hidden status B"],
        key="hidden-status-tabs",
    )
    with status_a:
        st.write("hidden status a")
    with status_b:
        st.write("hidden status b")

with st.expander("Expanded expander", expanded=True):
    visible_a, visible_b = st.tabs(
        ["Visible A", "Visible B"],
        key="visible-tabs",
    )
    with visible_a:
        st.write("visible a")
    with visible_b:
        st.write("visible b")
""",
        encoding="utf-8",
    )
    runtime = Runtime(script)
    runtime.run_script()

    titles = {
        command.title
        for command in StuiApp(runtime).get_system_commands(None)
    }

    assert {"Switch tab: Visible A", "Switch tab: Visible B"} <= titles
    assert not any("Hidden expander" in title for title in titles)
    assert not any("Hidden status" in title for title in titles)
