from pathlib import Path

import stui as st
from stui.elements import BarChartElement, MetricElement
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
    assert [(point.label, point.value) for point in charts[1].points] == [
        ("value", 0.0),
    ]


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
    assert [(point.label, point.value) for point in charts[1].points] == [
        ("value", 0.0),
    ]
