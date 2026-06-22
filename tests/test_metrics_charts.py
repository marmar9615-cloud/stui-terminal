from pathlib import Path

import stui as st
from stui.app import StuiApp
from stui.elements import (
    BarChartElement,
    BarChartPoint,
    ErrorElement,
    LineChartElement,
    LineChartSeries,
    MetricElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def chart_elements(runtime: Runtime) -> list[BarChartElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, BarChartElement)
    ]


def line_chart_elements(runtime: Runtime) -> list[LineChartElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, LineChartElement)
    ]


def test_metric_is_public_and_records_label_value_delta(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.metric("Latency", "42 ms", delta="-3 ms")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert st.metric is not None
    assert isinstance(runtime.elements[0], MetricElement)
    assert runtime.elements[0].label == "Latency"
    assert runtime.elements[0].value == "42 ms"
    assert runtime.elements[0].delta == "-3 ms"


def test_bar_chart_accepts_list_and_dict_shapes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.bar_chart([2, 4, 1], width=12, height=2)
st.bar_chart({"passed": 8, "failed": 1, "note": "ignored"})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = chart_elements(runtime)

    assert charts[0].width == 12
    assert charts[0].height == 2
    assert [(point.label, point.value) for point in charts[0].points] == [
        ("0", 2.0),
        ("1", 4.0),
        ("2", 1.0),
    ]
    assert [(point.label, point.value) for point in charts[1].points] == [
        ("passed", 8.0),
        ("failed", 1.0),
    ]


def test_bar_chart_accepts_simple_list_of_dicts(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.bar_chart([
    {"name": "alpha", "score": 3},
    {"name": "beta", "score": 7},
    {"label": "gamma", "value": 5},
    {"name": "skip"},
])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    chart = chart_elements(runtime)[0]

    assert [(point.label, point.value) for point in chart.points] == [
        ("alpha", 3.0),
        ("beta", 7.0),
        ("gamma", 5.0),
    ]


def test_bar_chart_scalar_and_unsupported_data_fallback(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.bar_chart(9)
st.bar_chart(object())
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = chart_elements(runtime)

    assert [(point.label, point.value) for point in charts[0].points] == [
        ("value", 9.0),
    ]
    assert charts[1].points == ()
    assert charts[1].empty is True


def test_bar_chart_ignores_nan_and_infinite_values(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import math
import stui as st

st.bar_chart([1, math.nan, math.inf, -math.inf, 2])
st.bar_chart({"bad": math.nan})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = chart_elements(runtime)

    assert [(point.label, point.value) for point in charts[0].points] == [
        ("0", 1.0),
        ("4", 2.0),
    ]
    assert charts[1].points == ()
    assert charts[1].empty is True


def test_bar_chart_keeps_negative_and_zero_only_data(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.bar_chart([-3, 0, 5], width=8)
st.bar_chart([0, 0, 0])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = chart_elements(runtime)

    assert [(point.label, point.value) for point in charts[0].points] == [
        ("0", -3.0),
        ("1", 0.0),
        ("2", 5.0),
    ]
    assert [(point.label, point.value) for point in charts[1].points] == [
        ("0", 0.0),
        ("1", 0.0),
        ("2", 0.0),
    ]
    signed_render = StuiApp._render_bar_chart(charts[0]).plain
    zero_render = StuiApp._render_bar_chart(charts[1]).plain
    assert "-3" in signed_render
    assert "│" in signed_render
    assert zero_render.count("·") == 3


def test_bar_chart_render_handles_small_width_and_blank_labels() -> None:
    chart = BarChartElement(
        points=(
            BarChartPoint("", 2.0),
        ),
        width=1,
    )

    rendered = StuiApp._render_bar_chart(chart).plain

    assert "2" in rendered
    assert "█" in rendered


def test_bar_chart_invalid_data_renders_no_chart_data(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import math
import stui as st

st.bar_chart(object())
st.bar_chart({"bad": math.nan})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = chart_elements(runtime)

    assert [chart.empty for chart in charts] == [True, True]
    assert StuiApp._render_bar_chart(charts[0]).plain == "No chart data"
    assert StuiApp._render_bar_chart(charts[1]).plain == "No chart data"


def test_charts_reject_nonpositive_width_and_height(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.bar_chart([1, 2], width=0)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert len(runtime.elements) == 1
    assert isinstance(runtime.elements[0], ErrorElement)
    assert "st.bar_chart width must be a positive int or None" in (
        runtime.elements[0].traceback
    )

    script = write_script(
        tmp_path,
        """
import stui as st

st.line_chart([1, 2], height=-1)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert len(runtime.elements) == 1
    assert isinstance(runtime.elements[0], ErrorElement)
    assert "st.line_chart height must be a positive int or None" in (
        runtime.elements[0].traceback
    )


def test_charts_render_edge_finite_values() -> None:
    bar = BarChartElement(
        points=(
            BarChartPoint("huge-positive", 1e308),
            BarChartPoint("huge-negative", -1e308),
            BarChartPoint("tiny", 1e-308),
        ),
        width=6,
    )
    line = LineChartElement(
        series=(
            LineChartSeries("swing", (-1e308, 0.0, 1e308)),
            LineChartSeries("flat tiny", (1e-308, 1e-308)),
        ),
        width=3,
    )

    bar_rendered = StuiApp._render_bar_chart(bar).plain
    line_rendered = StuiApp._render_line_chart(line).plain

    assert "huge-posi..." in bar_rendered
    assert "huge-nega..." in bar_rendered
    assert "1e+308" in bar_rendered
    assert "swing" in line_rendered
    assert "1e+308" in line_rendered


def test_line_chart_accepts_list_and_dict_series(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.line_chart([1, 3, 2, 5], width=8)
st.line_chart({"alpha": [1, 2, 3], "beta": [3, float("nan"), 1]}, height=1)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = line_chart_elements(runtime)

    assert st.line_chart is not None
    assert charts[0].width == 8
    assert [(series.label, series.values) for series in charts[0].series] == [
        ("value", (1.0, 3.0, 2.0, 5.0)),
    ]
    assert [(series.label, series.values) for series in charts[1].series] == [
        ("alpha", (1.0, 2.0, 3.0)),
        ("beta", (3.0, 1.0)),
    ]
    assert StuiApp._render_line_chart(charts[0]).plain.endswith(" 5")
    assert StuiApp._render_line_chart(charts[1]).plain.count("\n") == 0


def test_line_chart_accepts_simple_list_of_dicts(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.line_chart([
    {"step": 1, "loss": 0.9, "accuracy": 0.3},
    {"step": 2, "loss": 0.4, "accuracy": 0.8},
    {"step": 3, "loss": "skip", "accuracy": 0.9},
])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    chart = line_chart_elements(runtime)[0]

    assert [(series.label, series.values) for series in chart.series] == [
        ("loss", (0.9, 0.4)),
        ("accuracy", (0.3, 0.8, 0.9)),
    ]


def test_line_chart_fallback_for_unsupported_and_all_invalid(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import math
import stui as st

st.line_chart(object())
st.line_chart({"bad": [math.nan, math.inf]})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    charts = line_chart_elements(runtime)

    assert charts[0].series == ()
    assert charts[0].empty is True
    assert charts[1].series == ()
    assert charts[1].empty is True
    assert StuiApp._render_line_chart(charts[0]).plain == "No chart data"
