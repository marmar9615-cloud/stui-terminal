import sys
from pathlib import Path

import pytest

from stui.elements import (
    ButtonElement,
    ErrorElement,
    SliderElement,
    TableElement,
    TextInputElement,
    WriteElement,
)
from stui.runtime import Runtime, get_current_runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def assert_no_current_runtime() -> None:
    with pytest.raises(RuntimeError, match="stui API calls"):
        get_current_runtime()


def test_runtime_context_cleanup_after_normal_run(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("ok")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert_no_current_runtime()


def test_runtime_context_cleanup_after_exception(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert_no_current_runtime()


def test_runtime_context_cleanup_after_rerun(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0
if st.session_state.count == 0:
    st.session_state.count += 1
    st.rerun()
st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], WriteElement)
    assert elements[0].text == "count = 1"
    assert_no_current_runtime()


def test_stop_halts_script_without_traceback_and_preserves_state(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
st.session_state.count = st.session_state.get("count", 0) + 1
st.stop()
st.write("after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [WriteElement]
    assert elements[0].text == "before"
    assert runtime.session_state.count == 1
    assert_no_current_runtime()


def test_stop_is_not_swallowed_by_user_exception_handler(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
try:
    st.stop()
except Exception:
    st.write("caught")
st.write("after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    write_texts = [
        element.text
        for element in elements
        if isinstance(element, WriteElement)
    ]
    assert write_texts == ["before"]


def test_rerun_is_not_swallowed_by_user_exception_handler(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0

try:
    if st.session_state.count == 0:
        st.session_state.count = 1
        st.rerun()
except Exception:
    st.write("caught")

st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    write_texts = [
        element.text
        for element in elements
        if isinstance(element, WriteElement)
    ]
    assert write_texts == ["count = 1"]


def test_script_dir_is_removed_from_sys_path_after_normal_run(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("ok")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert str(tmp_path) not in sys.path


def test_script_dir_is_removed_from_sys_path_after_exception(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert str(tmp_path) not in sys.path


def test_script_dir_is_removed_from_sys_path_after_rerun(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "ran" not in st.session_state:
    st.session_state.ran = True
    st.rerun()
st.write("done")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert str(tmp_path) not in sys.path


def test_script_dir_is_removed_when_script_mutates_sys_path(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import sys
from pathlib import Path

import stui as st

sys.path.insert(0, str(Path(__file__).parent))
st.write("ok")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert str(tmp_path) not in sys.path


def test_script_exception_renders_error_without_corrupting_session_state(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.session_state.count = "bad"
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)
    runtime.session_state.count = 3

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "RuntimeError: boom" in elements[0].traceback
    assert runtime.session_state.count == 3


def test_script_exception_rolls_back_common_mutable_session_state(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.session_state.events.append("bad")
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)
    runtime.session_state.events = []

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert runtime.session_state.events == []


def test_missing_script_renders_readable_error(tmp_path: Path) -> None:
    runtime = Runtime(tmp_path / "missing.py")

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "No such file or directory" in elements[0].traceback
    assert "runpy" not in elements[0].traceback


def test_syntax_error_renders_concise_error(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if True
    st.write("broken")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "SyntaxError: expected ':'" in elements[0].traceback
    assert "runpy" not in elements[0].traceback


def test_import_error_renders_script_frame_without_runpy_noise(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st
import missing_stui_test_module

st.write("unreachable")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "ModuleNotFoundError" in elements[0].traceback
    assert "missing_stui_test_module" in elements[0].traceback
    assert "app.py" in elements[0].traceback
    assert "runpy" not in elements[0].traceback


def test_can_rerun_successfully_after_script_exception(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if st.session_state.get("fail", True):
    raise RuntimeError("boom")

st.write("recovered")
""",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    runtime.session_state.fail = False
    second = runtime.run_script()

    assert isinstance(first[0], ErrorElement)
    assert isinstance(second[0], WriteElement)
    assert second[0].text == "recovered"


def test_enabled_widget_change_survives_later_script_exception(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.text_input("Name", value="Ada", key="name")
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("name", "Grace")
    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "RuntimeError: boom" in elements[0].traceback
    assert runtime.session_state["name"] == "Grace"


def test_duplicate_explicit_widget_key_renders_readable_error(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.slider("First", key="shared")
st.button("Second", key="shared")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert elements[0].traceback == (
        'Duplicate widget key "shared". '
        "Explicit widget keys must be unique within a single run."
    )
    assert "shared" not in runtime.session_state


def test_duplicate_key_error_does_not_commit_pending_widget_change(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.text_input("Name", value="Ada", key="shared")
st.button("Submit", key="shared")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("shared", "Grace")
    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "Duplicate widget key" in elements[0].traceback
    assert "shared" not in runtime.session_state


def test_api_usage_error_does_not_commit_pending_widget_change(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.text_input("Name", value="Ada", key="name")
st.columns(0)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("name", "Grace")
    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "st.columns(count)" in elements[0].traceback
    assert "name" not in runtime.session_state


def test_generated_keys_may_repeat_labels_without_duplicate_error(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.slider("x")
st.slider("x")
st.button("Go")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    keys = [
        element.key
        for element in elements
        if isinstance(element, (SliderElement, ButtonElement))
    ]
    assert keys == ["slider:x:0", "slider:x:1", "button:Go:0"]


def test_hidden_form_pending_value_is_discarded_on_submit(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

show_extra = st.session_state.get("show_extra", True)

with st.form("profile"):
    st.text_input("Name", value="Ada", key="name")
    if show_extra:
        st.text_input("Extra", value="", key="extra")
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("name =", st.session_state.get("name", "missing"))
st.write("extra =", st.session_state.get("extra", "missing"))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("extra", "Grace")
    runtime.run_script()
    runtime.session_state.show_extra = False
    runtime.press_button("form_submit_button:profile:Save:0")
    runtime.run_script()

    assert "extra" not in runtime.session_state
    assert "name" not in runtime.session_state


def test_button_one_shot_unchanged(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.press_button("button:Increment:0")
    runtime.run_script()
    runtime.run_script()

    assert runtime.session_state.count == 1


def test_rerun_exhaustion_restores_pre_run_session_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.session_state.count = st.session_state.get("count", 0) + 1
st.rerun()
""",
    )
    runtime = Runtime(script)
    runtime.session_state.count = 3

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert "10 consecutive rerun" in elements[0].traceback
    assert runtime.session_state.count == 3


def test_many_widgets_remain_stable_across_repeated_runs(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

for index in range(150):
    st.text_input(f"Item {index}", value=str(index), key=f"item_{index}")
st.write("done")
""",
    )
    runtime = Runtime(script)

    for _ in range(25):
        elements = runtime.run_script()
        assert not any(isinstance(element, ErrorElement) for element in elements)
        assert sum(isinstance(element, TextInputElement) for element in elements) == 150
        assert runtime.session_state["item_0"] == "0"
        assert runtime.session_state["item_149"] == "149"
        assert_no_current_runtime()


def test_large_table_output_stays_bounded_with_limits(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

rows = [
    {f"col_{col}": f"{row}:{col}" for col in range(40)}
    for row in range(500)
]
st.table(rows, max_rows=4, max_cols=3)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()
    table = next(element for element in elements if isinstance(element, TableElement))

    assert table.headers == ("col_0", "col_1", "col_2", "...")
    assert len(table.rows) == 5
    assert table.rows[-1] == ("+496 rows", "", "", "")
