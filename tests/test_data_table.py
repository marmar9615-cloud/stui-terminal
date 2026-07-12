import asyncio
from pathlib import Path

import pytest
from textual.widgets import DataTable

from stui.app import StuiApp
from stui.elements import DataTableElement, ErrorElement, WriteElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def data_tables(runtime: Runtime) -> list[DataTableElement]:
    return [
        element for element in runtime.elements if isinstance(element, DataTableElement)
    ]


def test_data_table_single_selection_returns_source_row_index(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

selected = st.data_table(
    [{"name": "Ada"}, {"name": "Grace"}],
    selection_mode="single",
    key="runs",
)
st.write("selected =", selected)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.session_state["runs"] is None

    runtime.set_widget_value("runs", 1)
    runtime.run_script()

    assert runtime.session_state["runs"] == 1
    write = next(
        element for element in runtime.elements if isinstance(element, WriteElement)
    )
    assert write.text == "selected = 1"


def test_data_table_defaults_to_non_selectable_keyed_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

selected = st.data_table(["alpha", "beta"])
st.write("selected =", selected)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("data_table:data:0", 1)
    runtime.run_script()

    assert runtime.session_state["data_table:data:0"] is None
    assert data_tables(runtime)[0].selection_mode is None


def test_data_table_supports_existing_table_shapes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

class Frame:
    columns = ("name", "score")

    def to_dict(self, orient):
        assert orient == "records"
        return [{"name": "frame", "score": 12}]

st.data_table([{"name": "Ada", "score": 10}], key="records")
st.data_table([[1, 2], [3, 4]], key="matrix")
st.data_table({"a": [1, 2], "b": [3]}, key="columns")
st.data_table("scalar", key="scalar")
st.data_table(Frame(), key="frame")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    tables = data_tables(runtime)
    assert [(table.headers, table.rows) for table in tables] == [
        (("name", "score"), (("Ada", "10"),)),
        (("col_1", "col_2"), (("1", "2"), ("3", "4"))),
        (("a", "b"), (("1", "3"), ("2", ""))),
        (("value",), (("scalar",),)),
        (("name", "score"), (("frame", "12"),)),
    ]


@pytest.mark.parametrize("data_source", ["[{}, {}]", "[[], []]"])
def test_data_table_empty_row_shapes_mount_and_select(
    tmp_path: Path,
    data_source: str,
) -> None:
    script = write_script(
        tmp_path,
        f"""
import stui as st

st.data_table(
    {data_source},
    selection_mode="single",
    key="rows",
    show_index=True,
    max_rows=2,
    max_cols=1,
)
""",
    )
    runtime = Runtime(script)
    runtime.run_script()
    table = data_tables(runtime)[0]

    assert table.headers == ("#", "value")
    assert table.rows == (("0", ""), ("1", ""))

    async def scenario() -> None:
        app = StuiApp(runtime)
        async with app.run_test(headless=True, size=(32, 12)) as pilot:
            await pilot.pause()
            widget = app.query_one(DataTable)
            app.set_focus(widget)
            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state["rows"] == 0

    asyncio.run(scenario())


def test_data_table_limits_rows_and_columns_and_can_show_source_index(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

st.data_table(
    [
        {"a": 1, "b": 2, "c": 3},
        {"a": 4, "b": 5, "c": 6},
        {"a": 7, "b": 8, "c": 9},
    ],
    key="runs",
    selection_mode="single",
    max_rows=2,
    max_cols=2,
    height=6,
    show_index=True,
)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    table = data_tables(runtime)[0]
    assert table.headers == ("#", "a", "b", "...")
    assert table.rows == (
        ("0", "1", "2", "+1 cols"),
        ("1", "4", "5", "+1 cols"),
    )
    assert table.source_row_indices == (0, 1)
    assert table.hidden_rows == 1
    assert table.height == 6
    assert table.show_index is True


@pytest.mark.parametrize("value", [True, -1, 3, "1", 1.0])
def test_data_table_ignores_invalid_queued_selection_values(
    tmp_path: Path,
    value: object,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

if "events" not in st.session_state:
    st.session_state.events = []

def selected():
    st.session_state.events.append(st.session_state["runs"])

st.data_table(
    ["alpha", "beta", "gamma"],
    key="runs",
    selection_mode="single",
    on_select=selected,
)
""",
    )
    runtime = Runtime(script)
    runtime.run_script()
    runtime.set_widget_value("runs", 1)
    runtime.run_script()
    assert runtime.session_state["runs"] == 1
    assert runtime.session_state.events == [1]

    runtime.set_widget_value("runs", value)
    runtime.run_script()

    assert runtime.session_state["runs"] == 1
    assert runtime.session_state.events == [1]


def test_data_table_resets_only_when_source_rows_shrink(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

row_count = st.session_state.get("row_count", 3)
max_rows = st.session_state.get("max_rows")
st.data_table(
    list(range(row_count)),
    key="runs",
    selection_mode="single",
    max_rows=max_rows,
)
""",
    )
    runtime = Runtime(script)
    runtime.run_script()
    runtime.set_widget_value("runs", 2)
    runtime.run_script()
    assert runtime.session_state["runs"] == 2

    runtime.session_state.row_count = 2
    runtime.run_script()
    assert runtime.session_state["runs"] is None

    runtime.session_state.row_count = 3
    runtime.set_widget_value("runs", 2)
    runtime.run_script()
    runtime.session_state.max_rows = 2
    runtime.run_script()
    assert runtime.session_state["runs"] == 2


def test_data_table_disabled_ignores_pending_selection(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

st.data_table(
    ["alpha", "beta"],
    key="runs",
    selection_mode="single",
    disabled=True,
)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("runs", 1)
    runtime.run_script()

    assert runtime.session_state["runs"] is None
    assert data_tables(runtime)[0].disabled is True


def test_data_table_on_select_runs_after_state_update_with_arguments(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

if "events" not in st.session_state:
    st.session_state.events = []

def selected(prefix, *, suffix):
    st.session_state.events.append(
        f"{prefix}:{st.session_state['runs']}:{suffix}"
    )

st.data_table(
    ["alpha", "beta"],
    key="runs",
    selection_mode="single",
    on_select=selected,
    args=("picked",),
    kwargs={"suffix": "done"},
)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state.events == []

    runtime.set_widget_value("runs", 1)
    runtime.run_script()

    assert runtime.session_state["runs"] == 1
    assert runtime.session_state.events == ["picked:1:done"]


def test_data_table_inside_form_defers_state_and_callback_until_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

if "events" not in st.session_state:
    st.session_state.events = []

def selected():
    st.session_state.events.append(st.session_state["runs"])

with st.form("review"):
    selected_row = st.data_table(
        ["alpha", "beta"],
        key="runs",
        selection_mode="single",
        on_select=selected,
    )
    st.form_submit_button("Save")

st.write("selected =", selected_row)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("runs", 1)
    runtime.run_script()

    assert "runs" not in runtime.session_state
    assert runtime.session_state.events == []
    assert any(
        isinstance(element, WriteElement) and element.text == "selected = 1"
        for element in runtime.elements
    )

    runtime.press_button("form_submit_button:review:Save:0")
    runtime.run_script()

    assert runtime.session_state["runs"] == 1
    assert runtime.session_state.events == [1]


def test_data_table_form_drops_pending_selection_after_source_shrinks(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

row_count = st.session_state.get("row_count", 3)
with st.form("review"):
    selected = st.data_table(
        list(range(row_count)),
        key="runs",
        selection_mode="single",
    )
    st.form_submit_button("Save")

st.write("selected =", selected)
""",
    )
    runtime = Runtime(script)
    runtime.run_script()
    runtime.set_widget_value("runs", 2)
    runtime.run_script()
    assert runtime.form_pending_values["review"]["runs"] == 2

    runtime.session_state.row_count = 2
    runtime.run_script()
    assert any(
        isinstance(element, WriteElement) and element.text == "selected = None"
        for element in runtime.elements
    )

    runtime.press_button("form_submit_button:review:Save:0")
    runtime.run_script()

    assert "runs" not in runtime.session_state

    runtime.session_state.runs = 1
    runtime.session_state.row_count = 1
    runtime.run_script()

    assert runtime.session_state["runs"] is None


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (
            'selection_mode="multiple"',
            'st.data_table selection_mode must be None or "single".',
        ),
        ("max_rows=0", "st.data_table max_rows must be a positive integer or None."),
        ("max_cols=True", "st.data_table max_cols must be a positive integer or None."),
        ("height=0", "st.data_table height must be a positive integer or None."),
        ("show_index=1", "st.data_table show_index must be a bool."),
    ],
)
def test_data_table_rejects_invalid_options(
    tmp_path: Path,
    arguments: str,
    message: str,
) -> None:
    script = write_script(
        tmp_path,
        f"""
import stui.api as st

st.data_table([1, 2], {arguments})
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert elements == [ErrorElement(message)]


def test_textual_data_table_keyboard_selection_preserves_and_clamps_cursor(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

row_count = st.session_state.get("row_count", 3)
st.data_table(
    [f"row-{index}" for index in range(row_count)],
    key="runs",
    selection_mode="single",
)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(60, 18)) as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.cursor_type == "row"
            assert table.row_count == 3
            app.set_focus(table)

            await pilot.press("down", "enter")
            await pilot.pause()

            assert runtime.session_state["runs"] == 1
            table = app.query_one(DataTable)
            assert table.cursor_row == 1

            await pilot.press("down", "space")
            await pilot.pause()

            assert runtime.session_state["runs"] == 2
            table = app.query_one(DataTable)
            assert table.cursor_row == 2

            await pilot.press("r")
            await pilot.pause()
            assert app.query_one(DataTable).cursor_row == 2

            runtime.session_state.row_count = 1
            await app.action_rerun_script()
            await pilot.pause()

            table = app.query_one(DataTable)
            assert table.row_count == 1
            assert table.cursor_row == 0
            assert runtime.session_state["runs"] is None

    asyncio.run(scenario())


def test_textual_data_table_static_mode_is_focusable_but_disabled_mode_is_not(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

st.session_state.runs = st.session_state.get("runs", 0) + 1
st.data_table(["static"], key="static")
st.data_table(
    ["disabled"],
    key="disabled",
    selection_mode="single",
    disabled=True,
)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            static, disabled = app.query(DataTable)

            assert static.show_cursor is False
            assert static.can_focus is True
            assert disabled.disabled is True
            assert disabled.can_focus is False
            assert runtime.session_state["static"] is None
            assert runtime.session_state["disabled"] is None

            app.set_focus(None)
            await pilot.press("tab", "tab")
            assert app.focused is static

            await pilot.press("enter", "space")
            await pilot.pause()
            assert runtime.session_state["runs"] == 1
            assert runtime.session_state["static"] is None

    asyncio.run(scenario())


def test_textual_data_table_handles_unicode_multiline_long_and_narrow_content(
    tmp_path: Path,
) -> None:
    long_value = "x" * 200
    script = write_script(
        tmp_path,
        f"""\
import stui.api as st

st.data_table(
    [
        {{"name": "Ada\\nLovelace", "city": "東京", "note": {long_value!r}}},
        {{"name": "Grace", "city": "Zürich", "note": "second"}},
        {{"name": "Lin", "city": "台北", "note": "third"}},
    ],
    key="people",
    selection_mode="single",
    max_rows=2,
    height=5,
)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(24, 12)) as pilot:
            await pilot.pause()
            element = data_tables(runtime)[0]
            table = app.query_one(DataTable)

            assert element.rows[0] == ("Ada / Lovelace", "東京", long_value)
            assert element.hidden_rows == 1
            assert table.row_count == 2
            assert table.size.width <= 24
            assert table.size.height == 5

    asyncio.run(scenario())


def test_textual_data_table_mounts_and_selects_inside_columns(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

left, right = st.columns(2)
with left:
    st.data_table(
        [{"name": "Ada"}, {"name": "Grace"}],
        key="people",
        selection_mode="single",
    )
with right:
    st.write("details")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(100, 20)) as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.size.width < 60

            app.set_focus(table)
            await pilot.press("down", "enter")
            await pilot.pause()

            assert runtime.session_state["people"] == 1
            assert app.query_one(DataTable).cursor_row == 1

    asyncio.run(scenario())


def test_data_table_preserves_selection_when_row_contents_change(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

suffix = st.session_state.get("suffix", "old")
selected = st.data_table(
    [f"first-{suffix}", f"second-{suffix}"],
    key="runs",
    selection_mode="single",
)
st.write("selected =", selected)
""",
    )
    runtime = Runtime(script)
    runtime.run_script()
    runtime.set_widget_value("runs", 1)
    runtime.run_script()

    runtime.session_state.suffix = "new"
    runtime.run_script()

    assert runtime.session_state["runs"] == 1
    assert data_tables(runtime)[0].rows == (("first-new",), ("second-new",))


def test_textual_data_table_form_selection_commits_on_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

with st.form("review"):
    selected = st.data_table(
        ["alpha", "beta"],
        key="runs",
        selection_mode="single",
    )
    st.form_submit_button("Save")

st.write("selected =", selected)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            app.set_focus(table)

            await pilot.press("down", "enter")
            await pilot.pause()

            assert "runs" not in runtime.session_state
            assert any(
                isinstance(element, WriteElement) and element.text == "selected = 1"
                for element in runtime.elements
            )

            await pilot.press("tab", "enter")
            await pilot.pause()

            assert runtime.session_state["runs"] == 1

    asyncio.run(scenario())


def test_textual_data_table_empty_rows_are_not_focusable(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

st.data_table([], key="empty", selection_mode="single")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)

            assert table.row_count == 0
            assert table.can_focus is False
            assert table.show_cursor is False
            assert runtime.session_state["empty"] is None

    asyncio.run(scenario())


def test_textual_data_table_mouse_can_select_visible_source_row(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui.api as st

st.data_table(
    ["alpha", "beta", "gamma"],
    key="runs",
    selection_mode="single",
)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(60, 16)) as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.size.height >= 4, (table.size, table.region)
            widget_at, _ = app.get_widget_at(table.region.x + 2, table.region.y + 2)
            assert widget_at is table, (widget_at, table.region)

            highlighted = await pilot.click(table, offset=(2, 2))
            selected = await pilot.click(table, offset=(2, 2))
            await pilot.pause()

            assert highlighted is True
            assert selected is True
            assert runtime.session_state["runs"] == 1

    asyncio.run(scenario())
