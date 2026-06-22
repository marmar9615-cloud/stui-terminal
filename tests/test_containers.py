import asyncio
from pathlib import Path

from stui.app import StuiApp
from stui.elements import (
    ButtonElement,
    ColumnsElement,
    ContainerElement,
    ErrorElement,
    ExpanderElement,
    SliderElement,
    TextElement,
    WriteElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_container_context_preserves_order_and_children(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
with st.container():
    st.text("inside")
st.write("after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        WriteElement,
        ContainerElement,
        WriteElement,
    ]
    assert elements[0].text == "before"
    assert isinstance(elements[1].children[0], TextElement)
    assert elements[1].children[0].body == "inside"
    assert elements[2].text == "after"


def test_columns_preserve_column_children_and_order(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
left, right = st.columns(2)
with left:
    st.write("left")
with right:
    st.text("right")
st.write("after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        WriteElement,
        ColumnsElement,
        WriteElement,
    ]
    columns = elements[1]
    assert isinstance(columns, ColumnsElement)
    assert len(columns.columns) == 2
    assert isinstance(columns.columns[0][0], WriteElement)
    assert columns.columns[0][0].text == "left"
    assert isinstance(columns.columns[1][0], TextElement)
    assert columns.columns[1][0].body == "right"
    assert elements[2].text == "after"


def test_columns_support_nested_grouping(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

left, right = st.columns(2)
with left:
    with st.container():
        st.write("nested")
with right:
    with st.expander("Details", expanded=True):
        st.write("open")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    columns = elements[0]
    assert isinstance(columns, ColumnsElement)
    assert isinstance(columns.columns[0][0], ContainerElement)
    nested = columns.columns[0][0]
    assert isinstance(nested.children[0], WriteElement)
    assert nested.children[0].text == "nested"
    assert isinstance(columns.columns[1][0], ExpanderElement)
    expander = columns.columns[1][0]
    assert expander.children is not None
    assert isinstance(expander.children[0], WriteElement)
    assert expander.children[0].text == "open"


def test_columns_preserve_nested_interactive_content(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.container():
    left, right = st.columns(2)
    with left:
        st.button("Left", key="left")
    with right:
        with st.expander("Tools", expanded=True):
            st.slider("Amount", 0, 10, 5, key="amount")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    container = elements[0]
    assert isinstance(container, ContainerElement)
    columns = container.children[0]
    assert isinstance(columns, ColumnsElement)
    assert isinstance(columns.columns[0][0], ButtonElement)
    assert columns.columns[0][0].key == "left"
    expander = columns.columns[1][0]
    assert isinstance(expander, ExpanderElement)
    assert expander.children is not None
    assert isinstance(expander.children[0], SliderElement)
    assert expander.children[0].key == "amount"


def test_columns_reject_non_positive_counts(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.columns(0)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert "positive integer count" in elements[0].traceback


def test_columns_reject_streamlit_style_ratio_lists(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.columns([1, 2])
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert elements[0].traceback == (
        "st.columns(count) requires a positive integer count."
    )


def test_nested_container_and_expander_keep_nesting(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.container():
    st.write("outer")
    with st.expander("Details", expanded=True):
        st.write("inner")
    st.write("tail")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    container = elements[0]
    assert isinstance(container, ContainerElement)
    assert [type(element) for element in container.children] == [
        WriteElement,
        ExpanderElement,
        WriteElement,
    ]
    expander = container.children[1]
    assert isinstance(expander, ExpanderElement)
    assert expander.label == "Details"
    assert expander.key == "expander:Details:0"
    assert expander.expanded is True
    assert expander.children is not None
    assert isinstance(expander.children[0], WriteElement)
    assert expander.children[0].text == "inner"


def test_expander_defaults_to_static_closed(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Closed"):
    st.write("hidden for now")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ExpanderElement)
    assert elements[0].label == "Closed"
    assert elements[0].key == "expander:Closed:0"
    assert elements[0].expanded is False
    assert runtime.session_state["expander:Closed:0"] is False
    assert elements[0].children is not None
    assert isinstance(elements[0].children[0], WriteElement)


def test_expander_default_expanded_state_persists(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Open by default", expanded=True):
    st.write("visible")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], ExpanderElement)
    assert elements[0].expanded is True
    assert runtime.session_state["expander:Open by default:0"] is True


def test_expander_toggle_persists_in_session_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Details"):
    st.write("child")
""",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    runtime.set_widget_value("expander:Details:0", True)
    second = runtime.run_script()
    third = runtime.run_script()

    assert isinstance(first[0], ExpanderElement)
    assert first[0].expanded is False
    assert isinstance(second[0], ExpanderElement)
    assert second[0].expanded is True
    assert isinstance(third[0], ExpanderElement)
    assert third[0].expanded is True
    assert runtime.session_state["expander:Details:0"] is True


def test_expander_explicit_key_controls_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Details", key="details-open"):
    st.write("child")
""",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    runtime.set_widget_value("details-open", True)
    second = runtime.run_script()

    assert isinstance(first[0], ExpanderElement)
    assert first[0].key == "details-open"
    assert first[0].expanded is False
    assert isinstance(second[0], ExpanderElement)
    assert second[0].key == "details-open"
    assert second[0].expanded is True
    assert runtime.session_state["details-open"] is True


def test_nested_expander_content_render_order(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Outer", expanded=True):
    st.write("outer before")
    with st.expander("Inner", expanded=True):
        st.write("inner")
    st.write("outer after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    outer = elements[0]
    assert isinstance(outer, ExpanderElement)
    assert [type(element) for element in (outer.children or [])] == [
        WriteElement,
        ExpanderElement,
        WriteElement,
    ]
    inner = outer.children[1]
    assert isinstance(inner, ExpanderElement)
    assert inner.children is not None
    assert isinstance(inner.children[0], WriteElement)
    assert inner.children[0].text == "inner"
    assert outer.children[0].text == "outer before"
    assert outer.children[2].text == "outer after"


def test_container_context_stack_unwinds_after_script_error(tmp_path: Path) -> None:
    failing = write_script(
        tmp_path,
        """
import stui as st

with st.container():
    raise RuntimeError("boom")
""",
    )
    succeeding = write_script(
        tmp_path,
        """
import stui as st

st.write("ok")
""",
    )
    runtime = Runtime(failing)
    runtime.run_script()

    runtime.script_path = succeeding
    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], WriteElement)
    assert elements[0].text == "ok"


def test_static_expanders_render_open_and_closed(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Closed"):
    st.write("closed child")
with st.expander("Open", expanded=True):
    st.write("open child")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-expander"))) == 2
            assert len(list(app.query(".write"))) == 1

    asyncio.run(scenario())


def test_textual_columns_stack_on_narrow_terminals(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

left, right = st.columns(2)
with left:
    st.write("left")
with right:
    st.write("right")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(44, 20)) as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-columns-stacked"))) == 1
            assert len(list(app.query(".stui-column"))) == 2
            assert len(list(app.query(".write"))) == 2

    asyncio.run(scenario())


def test_deep_nested_layout_renders_in_very_narrow_terminal(tmp_path: Path) -> None:
    long_label = "Details " + ("x" * 120)
    script = write_script(
        tmp_path,
        f"""
import stui as st

left, right = st.columns(2)
with left:
    with st.container():
        with st.expander("{long_label}", expanded=True):
            st.write("left nested")
with right:
    with st.expander("{long_label}", expanded=True):
        with st.container():
            st.write("right nested")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(24, 18)) as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-columns-stacked"))) == 1
            assert len(list(app.query(".stui-expander"))) == 2
            assert len(list(app.query(".write"))) == 2

    asyncio.run(scenario())


def test_textual_columns_render_side_by_side_when_wide(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

left, middle, right = st.columns(3)
with left:
    st.write("left")
with middle:
    st.write("middle")
with right:
    st.write("right")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(120, 24)) as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-columns"))) == 1
            assert len(list(app.query(".stui-columns-stacked"))) == 0
            assert len(list(app.query(".stui-column"))) == 3
            assert len(list(app.query(".write"))) == 3

    asyncio.run(scenario())


def test_nested_columns_stack_against_parent_column_width(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

left, right = st.columns(2)
with left:
    inner_left, inner_right = st.columns(2)
    with inner_left:
        st.write("inner left")
    with inner_right:
        st.write("inner right")
with right:
    st.write("outer right")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-columns"))) == 2
            assert len(list(app.query(".stui-columns-stacked"))) == 1
            assert len(list(app.query(".stui-column"))) == 4
            assert len(list(app.query(".write"))) == 3

    asyncio.run(scenario())


def test_textual_expander_keyboard_toggle_persists(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
with st.expander("Details"):
    st.write("child")
st.write("after")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["expander:Details:0"] is False
            assert len(list(app.query(".write"))) == 2

            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()

            assert runtime.session_state["expander:Details:0"] is True
            assert runtime.last_focused_key == "expander:Details:0"
            assert getattr(app.focused, "stui_key", None) == "expander:Details:0"
            assert len(list(app.query(".write"))) == 3

            await pilot.press("space")
            await pilot.pause()

            assert runtime.session_state["expander:Details:0"] is False
            assert len(list(app.query(".write"))) == 2

    asyncio.run(scenario())
