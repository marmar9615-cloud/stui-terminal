import asyncio
import inspect
from pathlib import Path

import pytest
from textual.widgets import Tab, Tabs

from stui.app import StuiApp, dom_id_for_key
from stui.elements import ErrorElement, WriteElement
from stui.runtime import Runtime
from stui.tabs import tabs


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def rendered_writes(app: StuiApp) -> list[str]:
    return [widget.content.plain for widget in app.query(".write")]


def test_tabs_wrapper_has_the_experimental_public_signature() -> None:
    signature = inspect.signature(tabs)

    assert list(signature.parameters) == [
        "labels",
        "key",
        "default",
        "on_change",
        "args",
        "kwargs",
    ]
    assert signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["key"].default is None
    assert signature.parameters["default"].default == 0
    assert signature.parameters["on_change"].default is None
    assert signature.parameters["args"].default is None
    assert signature.parameters["kwargs"].default is None


def test_all_tab_blocks_execute_and_collect_separate_panes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

overview, details = tabs(["Overview", "Details"], key="workspace")
with overview:
    st.session_state.overview_ran = True
    st.write("overview")
with details:
    st.session_state.details_ran = True
    st.write("details")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert runtime.session_state.overview_ran is True
    assert runtime.session_state.details_ran is True
    assert len(elements) == 1
    tabs_element = elements[0]
    assert type(tabs_element).__name__ == "TabsElement"
    assert tabs_element.labels == ("Overview", "Details")
    assert tabs_element.key == "workspace"
    assert tabs_element.active == 0
    assert [
        [child.text for child in pane if isinstance(child, WriteElement)]
        for pane in tabs_element.panes
    ] == [["overview"], ["details"]]


def test_generated_keys_are_stable_with_duplicate_labels(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
from stui.tabs import tabs

tabs(["Same", "Same"])
tabs(["Same", "Same"])
""",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    second = runtime.run_script()

    assert [element.key for element in first] == [
        "tabs:('Same', 'Same'):0",
        "tabs:('Same', 'Same'):1",
    ]
    assert [element.key for element in second] == [
        element.key for element in first
    ]
    assert [element.labels for element in second] == [
        ("Same", "Same"),
        ("Same", "Same"),
    ]


@pytest.mark.parametrize(
    "labels_expression",
    [
        "[]",
        "'Overview'",
        "['Overview', '']",
        "['Overview', '   ']",
        "['Overview', 3]",
        "{'Overview', 'Details'}",
        "None",
    ],
)
def test_invalid_labels_render_readable_error(
    tmp_path: Path,
    labels_expression: str,
) -> None:
    script = write_script(
        tmp_path,
        f"""
from stui.tabs import tabs

tabs({labels_expression})
""",
    )

    elements = Runtime(script).run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert elements[0].traceback == (
        "st.tabs(labels) requires a non-empty sequence of non-empty strings."
    )


@pytest.mark.parametrize("default", [-1, 2, True, 1.5])
def test_invalid_default_renders_readable_error(
    tmp_path: Path,
    default: object,
) -> None:
    script = write_script(
        tmp_path,
        f"""
from stui.tabs import tabs

tabs(["Overview", "Details"], default={default!r})
""",
    )

    elements = Runtime(script).run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert elements[0].traceback == (
        "st.tabs default must be an integer index between 0 and 1."
    )


def test_active_state_persists_and_callback_observes_new_index(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

tabs(
    ["Overview", "Details"],
    key="workspace",
    default=1,
    on_change=record,
    args=("workspace",),
    kwargs={"prefix": "tab"},
)
""",
    )
    runtime = Runtime(script)

    initial = runtime.run_script()
    assert initial[0].active == 1
    assert runtime.session_state["workspace"] == 1
    assert runtime.session_state.events == []

    runtime.set_widget_value("workspace", 0)
    changed = runtime.run_script()
    assert changed[0].active == 0
    assert runtime.session_state["workspace"] == 0
    assert runtime.session_state.events == ["tab:0"]

    unchanged = runtime.run_script()
    assert unchanged[0].active == 0
    assert runtime.session_state.events == ["tab:0"]


def test_stale_active_state_falls_back_to_default(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
from stui.tabs import tabs

tabs(["Overview", "Details"], key="workspace", default=1)
""",
    )
    runtime = Runtime(script)
    runtime.session_state["workspace"] = 9

    elements = runtime.run_script()

    assert elements[0].active == 1
    assert runtime.session_state["workspace"] == 1


def test_explicit_tab_key_collides_with_other_widget_types(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

tabs(["Overview", "Details"], key="shared")
st.button("Save", key="shared")
""",
    )

    elements = Runtime(script).run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert 'Duplicate widget key "shared"' in elements[0].traceback


def test_only_active_children_mount_and_hidden_widgets_skip_focus(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

overview, details = tabs(["Overview", "Details"], key="workspace")
with overview:
    st.write("overview")
    st.button("Visible", key="visible")
with details:
    st.write("details")
    st.button("Hidden", key="hidden")
st.button("After", key="after")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()

            assert len(list(app.query(Tabs))) == 1
            assert rendered_writes(app) == ["overview"]
            assert len(list(app.query(f"#{dom_id_for_key('visible')}"))) == 1
            assert len(list(app.query(f"#{dom_id_for_key('hidden')}"))) == 0

            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "workspace"
            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "visible"
            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "after"

    asyncio.run(scenario())


def test_left_right_keyboard_changes_tabs_and_restores_focus(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

overview, details = tabs(["Overview", "Details"], key="workspace")
with overview:
    st.write("overview")
with details:
    st.write("details")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "workspace"

            await pilot.press("right")
            await pilot.pause()
            assert runtime.session_state["workspace"] == 1
            assert rendered_writes(app) == ["details"]
            assert getattr(app.focused, "stui_key", None) == "workspace"

            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["workspace"] == 0
            assert rendered_writes(app) == ["overview"]

            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["workspace"] == 1
            assert rendered_writes(app) == ["details"]

    asyncio.run(scenario())


def test_mouse_selects_duplicate_label_by_index(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

first, second = tabs(["Same", "Same"], key="duplicates")
with first:
    st.write("first")
with second:
    st.write("second")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            tab_widgets = list(app.query(Tab))
            assert [tab.label_text for tab in tab_widgets] == ["Same", "Same"]

            clicked = await pilot.click(tab_widgets[1])
            await pilot.pause()

            assert clicked is True
            assert runtime.session_state["duplicates"] == 1
            assert rendered_writes(app) == ["second"]
            assert getattr(app.focused, "stui_key", None) == "duplicates"

    asyncio.run(scenario())


def test_nested_tabs_preserve_inner_state_across_outer_switches(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

outer_one, outer_two = tabs(["Outer one", "Outer two"], key="outer")
with outer_one:
    inner_one, inner_two = tabs(["Inner one", "Inner two"], key="inner")
    with inner_one:
        st.write("inner one")
    with inner_two:
        st.write("inner two")
with outer_two:
    st.write("outer two")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            assert len(list(app.query(Tabs))) == 2
            assert rendered_writes(app) == ["inner one"]

            await pilot.press("tab", "tab", "right")
            await pilot.pause()
            assert runtime.session_state["inner"] == 1
            assert rendered_writes(app) == ["inner two"]

            await pilot.press("shift+tab", "right")
            await pilot.pause()
            assert runtime.session_state["outer"] == 1
            assert len(list(app.query(Tabs))) == 1
            assert rendered_writes(app) == ["outer two"]

            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["outer"] == 0
            assert runtime.session_state["inner"] == 1
            assert len(list(app.query(Tabs))) == 2
            assert rendered_writes(app) == ["inner two"]

    asyncio.run(scenario())


def test_tabs_compose_with_containers_columns_expanders_and_forms(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

with st.container():
    left, right = st.columns(2)
    with left:
        with st.expander("Workspace", expanded=True):
            visible, hidden = tabs(["Visible", "Hidden"], key="layout-tabs")
            with visible:
                with st.form("visible-form"):
                    st.text_input("Visible field", key="visible-field")
                    st.form_submit_button("Save visible")
            with hidden:
                with st.form("hidden-form"):
                    st.text_input("Hidden field", key="hidden-field")
                    st.form_submit_button("Save hidden")
    with right:
        st.write("right column")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(120, 24)) as pilot:
            await pilot.pause()

            assert len(list(app.query(".stui-container"))) == 1
            assert len(list(app.query(".stui-columns"))) == 1
            assert len(list(app.query(".stui-expander"))) == 1
            assert len(list(app.query(Tabs))) == 1
            assert len(
                list(app.query(f"#{dom_id_for_key('visible-field')}"))
            ) == 1
            assert len(
                list(app.query(f"#{dom_id_for_key('hidden-field')}"))
            ) == 0

    asyncio.run(scenario())


def test_tabs_inside_form_defer_state_and_callback_until_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
from stui.tabs import tabs

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append(f"tab:{st.session_state['form-tabs']}")

with st.form("settings"):
    first, second = tabs(
        ["First", "Second"],
        key="form-tabs",
        on_change=record,
    )
    with first:
        st.text_input("First value", key="first-value")
    with second:
        st.text_input("Second value", key="second-value")
    st.form_submit_button("Apply")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(80, 30)) as pilot:
            await pilot.pause()
            assert "form-tabs" not in runtime.session_state
            assert runtime.session_state.events == []

            await pilot.press("tab", "right")
            await pilot.pause()
            assert "form-tabs" not in runtime.session_state
            assert runtime.session_state.events == []
            assert len(
                list(app.query(f"#{dom_id_for_key('first-value')}"))
            ) == 0
            assert len(
                list(app.query(f"#{dom_id_for_key('second-value')}"))
            ) == 1

            submit_key = "form_submit_button:settings:Apply:0"
            runtime.press_button(submit_key)
            runtime.run_script()
            await app.render_runtime()
            await pilot.pause()

            assert runtime.session_state["form-tabs"] == 1
            assert runtime.session_state.events == ["tab:1"]

    asyncio.run(scenario())


def test_tab_labels_escape_markup_and_terminal_controls(tmp_path: Path) -> None:
    unsafe_label = "[bold]unsafe[/bold]\x1b\tline\nnext"
    script = write_script(
        tmp_path,
        f"""
from stui.tabs import tabs

tabs([{unsafe_label!r}, "Safe"], key="safe-labels")
""",
    )

    async def scenario() -> None:
        app = StuiApp(Runtime(script))

        async with app.run_test(size=(80, 16)) as pilot:
            await pilot.pause()
            labels = [tab.label_text for tab in app.query(Tab)]
            assert labels == [
                "[bold]unsafe[/bold]\\x1b\\tline\\nnext",
                "Safe",
            ]

    asyncio.run(scenario())


def test_long_labels_remain_keyboard_usable_in_narrow_terminal(
    tmp_path: Path,
) -> None:
    long_label = "Long " + ("x" * 200)
    script = write_script(
        tmp_path,
        f"""
import stui as st
from stui.tabs import tabs

long_tab, short_tab = tabs([{long_label!r}, "Short"], key="narrow")
with long_tab:
    st.write("long")
with short_tab:
    st.write("short")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(20, 12)) as pilot:
            await pilot.pause()
            assert len(list(app.query(Tabs))) == 1
            assert len(list(app.query(Tab))[0].label_text) <= 72

            await pilot.press("tab", "right")
            await pilot.pause()
            assert runtime.session_state["narrow"] == 1
            assert rendered_writes(app) == ["short"]

    asyncio.run(scenario())
