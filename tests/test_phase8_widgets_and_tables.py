import json
from pathlib import Path

from stui.elements import (
    AlertElement,
    ErrorElement,
    JsonElement,
    NumberInputElement,
    ProgressElement,
    RadioElement,
    SelectboxElement,
    TableElement,
    WriteElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def writes(runtime: Runtime) -> list[str]:
    return [
        element.text
        for element in runtime.elements
        if isinstance(element, WriteElement)
    ]


def test_number_input_default_clamp_and_state_persistence(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

value = st.number_input("Batch", min_value=1, max_value=8, value=4, key="batch")
st.write("batch =", value)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["batch"] == 4
    assert isinstance(runtime.elements[0], NumberInputElement)

    runtime.set_widget_value("batch", 99)
    runtime.run_script()
    assert runtime.session_state["batch"] == 8
    assert writes(runtime) == ["batch = 8"]


def test_number_input_float_step_preserves_float_values(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

value = st.number_input("Temperature", value=0, step=0.1, key="temp")
st.write("temp =", value)
""",
    )
    runtime = Runtime(script)

    runtime.set_widget_value("temp", "0.7")
    runtime.run_script()

    assert runtime.session_state["temp"] == 0.7
    assert writes(runtime) == ["temp = 0.7"]


def test_selectbox_and_radio_defaults_and_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

model = st.selectbox("Model", ["tiny", "base", "large"], index=1, key="model")
mode = st.radio("Mode", ("fast", "quality"), key="mode")
st.write("model =", model)
st.write("mode =", mode)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["model"] == "base"
    assert runtime.session_state["mode"] == "fast"
    assert [type(element) for element in runtime.elements[:2]] == [
        SelectboxElement,
        RadioElement,
    ]

    runtime.set_widget_value("model", "large")
    runtime.set_widget_value("mode", "quality")
    runtime.run_script()
    assert writes(runtime) == ["model = large", "mode = quality"]


def test_choice_widgets_empty_options_render_error(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

value = st.selectbox("Empty", [])
st.write("value =", value)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert isinstance(runtime.elements[0], AlertElement)
    assert runtime.elements[0].kind == "error"
    assert "requires at least one option" in runtime.elements[0].body
    assert writes(runtime) == ["value = None"]


def test_empty_choice_widget_inside_form_does_not_commit_before_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("choices"):
    value = st.selectbox("Choice", [], key="choice")
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("value =", value)
st.write("state =", st.session_state.get("choice", "missing"))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert isinstance(runtime.elements[0], AlertElement)
    assert writes(runtime) == [
        "submitted = False",
        "value = None",
        "state = missing",
    ]
    assert "choice" not in runtime.session_state


def test_empty_selectbox_inside_form_clears_stale_state_on_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

empty = st.session_state.get("empty", False)

with st.form("choices"):
    options = [] if empty else ["a", "b"]
    value = st.selectbox("Choice", options, key="choice")
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("value =", value)
st.write("state =", st.session_state.get("choice", "missing"))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("choice", "b")
    runtime.press_button("form_submit_button:choices:Save:0")
    runtime.run_script()
    assert runtime.session_state["choice"] == "b"

    runtime.session_state.empty = True
    runtime.run_script()
    assert isinstance(runtime.elements[0], AlertElement)
    assert writes(runtime) == [
        "submitted = False",
        "value = None",
        "state = b",
    ]

    runtime.press_button("form_submit_button:choices:Save:0")
    runtime.run_script()

    assert writes(runtime) == [
        "submitted = True",
        "value = None",
        "state = None",
    ]
    assert runtime.session_state["choice"] is None


def test_new_widget_callbacks_and_disabled_behavior(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

st.number_input("N", key="n", on_change=record, args=("n",), kwargs={"prefix": "n"})
st.selectbox(
    "S",
    ["a", "b"],
    key="s",
    on_change=record,
    args=("s",),
    kwargs={"prefix": "s"},
)
st.radio(
    "R",
    ["x", "y"],
    key="r",
    disabled=True,
    on_change=record,
    args=("r",),
    kwargs={"prefix": "r"},
)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("n", 5)
    runtime.set_widget_value("s", "b")
    runtime.set_widget_value("r", "y")
    runtime.run_script()

    assert writes(runtime) == ["events = n:5,s:b"]


def test_table_supported_shapes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table([{"name": "Ada", "score": 10}, {"name": "Grace", "score": 11}])
st.table([[1, 2], [3, 4]])
st.table({"a": [1, 2], "b": [3]})
st.dataframe("scalar")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()
    tables = [element for element in elements if isinstance(element, TableElement)]

    assert tables[0].headers == ("name", "score")
    assert tables[0].rows == (("Ada", "10"), ("Grace", "11"))
    assert tables[1].headers == ("col_1", "col_2")
    assert tables[1].rows == (("1", "2"), ("3", "4"))
    assert tables[2].headers == ("a", "b")
    assert tables[2].rows == (("1", "3"), ("2", ""))
    assert tables[3].headers == ("value",)
    assert tables[3].rows == (("scalar",),)


def test_table_max_rows_and_max_cols_add_truncation_markers(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table(
    [
        {"a": 1, "b": 2, "c": 3, "d": 4},
        {"a": 5, "b": 6, "c": 7, "d": 8},
        {"a": 9, "b": 10, "c": 11, "d": 12},
    ],
    max_rows=2,
    max_cols=2,
)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("a", "b", "...")
    assert table.rows == (
        ("1", "2", "+2 cols"),
        ("5", "6", "+2 cols"),
        ("+1 rows", "", ""),
    )


def test_table_rejects_invalid_max_rows_and_max_cols(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table([1, 2, 3], max_rows=0)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert len(runtime.elements) == 1
    assert isinstance(runtime.elements[0], ErrorElement)
    assert "st.table max_rows must be a positive integer or None" in (
        runtime.elements[0].traceback
    )


def test_table_list_of_dicts_preserves_non_string_keys(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table([{1: "one", "two": 2}, {1: "uno"}])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("1", "two")
    assert table.rows == (("one", "2"), ("uno", ""))


def test_table_empty_column_dict_preserves_headers(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table({"a": [], "b": []})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("a", "b")
    assert table.rows == ()


def test_table_uneven_list_rows_pad_missing_cells(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table([[1, 2, 3], [4]])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("col_1", "col_2", "col_3")
    assert table.rows == (("1", "2", "3"), ("4", "", ""))


def test_table_supports_dataclasses_namedtuples_and_public_objects(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
from collections import namedtuple
from dataclasses import dataclass
import stui as st

@dataclass
class Run:
    name: str
    score: float

Point = namedtuple("Point", ["x", "y"])

class PublicAttrs:
    def __init__(self):
        self.name = "attrs"
        self.count = 3
        self._private = "hidden"

st.table([Run("baseline", 0.81), Run("candidate", 0.88)])
st.table([Point(1, 2), Point(3, 4)])
st.table([PublicAttrs()])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    tables = [
        element
        for element in runtime.elements
        if isinstance(element, TableElement)
    ]

    assert tables[0].headers == ("name", "score")
    assert tables[0].rows == (("baseline", "0.81"), ("candidate", "0.88"))
    assert tables[1].headers == ("x", "y")
    assert tables[1].rows == (("1", "2"), ("3", "4"))
    assert tables[2].headers == ("name", "count")
    assert tables[2].rows == (("attrs", "3"),)


def test_table_normalizes_multiline_and_tabbed_cells(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table([
    {"name": "Ada\\nLovelace", "note": "fast\\tpath"},
    {"name": "Grace", "note": "line one\\nline two"},
])
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("name", "note")
    assert table.rows == (
        ("Ada / Lovelace", "fast    path"),
        ("Grace", "line one / line two"),
    )


def test_dataframe_preserves_empty_declared_columns_without_pandas(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

class Frame:
    columns = ("name", "score")

    def to_dict(self, orient):
        assert orient == "records"
        return []

st.dataframe(Frame())
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("name", "score")
    assert table.rows == ()


def test_dataframe_declared_columns_fill_missing_record_keys(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

class Frame:
    columns = ("name", "score", "status")

    def to_dict(self, orient):
        assert orient == "records"
        return [{"name": "Ada", "score": 10}, {"name": "Grace", "status": "ok"}]

st.dataframe(Frame(), max_cols=2)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("name", "score", "...")
    assert table.rows == (("Ada", "10", "+1 cols"), ("Grace", "", "+1 cols"))


def test_json_progress_and_dataframe_stable_fallbacks(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

class Thing:
    def __str__(self):
        return "thing-as-text"

st.json({"item": Thing()})
st.progress(1.5, text="over")
st.progress(-10)
st.dataframe({"name": ["Ada"], "score": [10]})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    json_element = next(
        element for element in runtime.elements if isinstance(element, JsonElement)
    )
    progress = [
        element for element in runtime.elements if isinstance(element, ProgressElement)
    ]
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert '"thing-as-text"' in json_element.text
    assert [element.value for element in progress] == [2, 0]
    assert progress[0].text == "over"
    assert table.headers == ("name", "score")
    assert table.rows == (("Ada", "10"),)


def test_json_handles_mixed_and_non_string_mapping_keys(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.json({("x",): 1, 2: "two", "three": {"nested": object()}})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    json_element = next(
        element for element in runtime.elements if isinstance(element, JsonElement)
    )

    rendered = json.loads(json_element.text)
    assert rendered["('x',)"] == 1
    assert rendered["2"] == "two"
    assert "nested" in rendered["three"]


def test_progress_rejects_bool_and_non_finite_values(tmp_path: Path) -> None:
    for expression, message in [
        ("True", "st.progress value must be an int or float."),
        ('float("nan")', "st.progress value must be finite."),
        ('float("inf")', "st.progress value must be finite."),
    ]:
        script = write_script(
            tmp_path,
            f"""
import stui as st

st.progress({expression})
""",
        )
        runtime = Runtime(script)

        elements = runtime.run_script()

        assert len(elements) == 1
        assert isinstance(elements[0], ErrorElement)
        assert elements[0].traceback == message


def test_table_additional_stable_shapes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.table({"a": 1, "b": 2})
st.table(["a", 1])
st.table([])
st.table({})
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    tables = [
        element
        for element in runtime.elements
        if isinstance(element, TableElement)
    ]

    assert tables[0].headers == ("key", "value")
    assert tables[0].rows == (("a", "1"), ("b", "2"))
    assert tables[1].headers == ("value",)
    assert tables[1].rows == (("a",), ("1",))
    assert tables[2].headers == ("value",)
    assert tables[2].rows == ()
    assert tables[3].headers == ("key", "value")
    assert tables[3].rows == ()


def test_dataframe_duck_typing_without_pandas_dependency(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

class TinyFrame:
    columns = ("name", "score")

    def to_dict(self, orient):
        assert orient == "records"
        return [{"name": "Ada", "score": 10}]

st.dataframe(TinyFrame())
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    table = next(
        element for element in runtime.elements if isinstance(element, TableElement)
    )

    assert table.headers == ("name", "score")
    assert table.rows == (("Ada", "10"),)
