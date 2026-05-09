import sys
from pathlib import Path

import pytest

from stui.elements import ButtonElement, ErrorElement, SliderElement, WriteElement
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
