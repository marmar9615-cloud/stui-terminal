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
