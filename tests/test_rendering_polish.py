import asyncio
from pathlib import Path

from rich.console import Console

from stui.app import StuiApp, StuiSelectbox
from stui.elements import (
    BarChartElement,
    BarChartPoint,
    LineChartElement,
    LineChartSeries,
    SelectboxElement,
    StatusElement,
    TableElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_wide_table_trims_columns_for_narrow_width() -> None:
    table = TableElement(
        headers=tuple(f"column_{index}" for index in range(12)),
        rows=(tuple(f"value_{index}" for index in range(12)),),
    )

    headers, rows = StuiApp._trim_table(table.headers, table.rows, 24)
    rendered = StuiApp._render_table(table, 24)
    console = Console(width=24, record=True)
    console.print(rendered)

    assert headers == ("column_0", "column_1", "column_2", "...")
    assert rows == (("value_0", "value_1", "value_2", "+9 cols"),)
    exported = console.export_text()
    assert "+9" in exported
    assert "col" in exported


def test_dataframe_wide_dict_trims_without_dropping_row_values(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.dataframe({f"column_{index}": [index] for index in range(20)})
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()
    table = elements[0]
    assert isinstance(table, TableElement)

    headers, rows = StuiApp._trim_table(table.headers, table.rows, 30)

    assert headers == ("column_0", "column_1", "column_2", "column_3", "...")
    assert rows == (("0", "1", "2", "3", "+16 cols"),)


def test_table_warns_in_ultra_narrow_width() -> None:
    table = TableElement(
        headers=("alpha", "beta", "gamma"),
        rows=(("one", "two", "three"),),
    )

    rendered = StuiApp._render_table(table, 12)

    assert rendered.plain == "Table requires a wider terminal."


def test_chart_renderers_handle_one_column_width_and_long_labels() -> None:
    long_label = "dataset-" + ("x" * 80)
    bar = BarChartElement(
        points=(BarChartPoint(long_label, 3.0), BarChartPoint("zero", 0.0)),
        width=1,
    )
    line = LineChartElement(
        series=(LineChartSeries(long_label, (1.0, 2.0, 3.0)),),
        width=1,
    )

    bar_text = StuiApp._render_bar_chart(bar).plain
    line_text = StuiApp._render_line_chart(line).plain

    assert "..." in bar_text
    assert "█" in bar_text
    assert "..." in line_text
    assert line_text.endswith(" 3")


def test_selectbox_render_value_clips_long_option() -> None:
    widget = StuiSelectbox(
        SelectboxElement(
            label="Model",
            key="model",
            options=("choice-" + ("x" * 120),),
            index=0,
        )
    )

    rendered = widget._render_value()

    assert len(rendered) < 80
    assert rendered.endswith("... ]")


def test_panels_with_long_text_render_in_tiny_terminal_without_traceback(
    tmp_path: Path,
) -> None:
    long_text = "help " + ("x" * 300)
    script = write_script(
        tmp_path,
        f"""
import stui as st

with st.status("{long_text}", expanded=True):
    st.help("{long_text}")
try:
    raise RuntimeError("{"frame_with_a_very_long_name " * 20}")
except RuntimeError as exc:
    st.exception(exc)
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(16, 12)) as pilot:
            await pilot.pause()
            assert list(app.query(".stui-status"))
            assert len(list(app.query(".stui-help"))) == 1
            assert len(list(app.query(".exception"))) == 1
            assert not list(app.query(".error"))

    asyncio.run(scenario())


def test_status_spinner_help_and_table_render_in_narrow_terminal(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.status("Loading narrow data", state="complete", expanded=True):
    st.table({f"col_{index}": [index] for index in range(10)})
with st.spinner("Finalizing"):
    st.help("Small terminal help text")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(18, 14)) as pilot:
            await pilot.pause()
            assert isinstance(runtime.elements[0], StatusElement)
            assert not list(app.query(".error"))
            assert len(list(app.query(".stui-status"))) >= 1
            assert len(list(app.query(".stui-spinner"))) >= 1
            assert len(list(app.query(".stui-help"))) == 1

    asyncio.run(scenario())


def test_long_labels_render_in_narrow_app_without_traceback(tmp_path: Path) -> None:
    long_label = "Label " + ("x" * 160)
    script = write_script(
        tmp_path,
        f"""
import stui as st

st.metric("{long_label}", "1234567890", delta="+9999999999")
st.warning("{long_label}")
with st.form("narrow"):
    st.text_input("{long_label}", value="Ada")
    st.selectbox("{long_label}", ["{"option-" + ("y" * 140)}"])
    st.radio("{long_label}", ["{"mode-" + ("z" * 140)}"])
    st.form_submit_button("{long_label}")
with st.expander("{long_label}", expanded=True):
    st.write("inside")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test(size=(24, 20)) as pilot:
            await pilot.pause()
            assert not list(app.query(".error"))
            assert len(list(app.query(".stui-field-label"))) == 3
            assert len(list(app.query(".stui-expander"))) == 1

    asyncio.run(scenario())
