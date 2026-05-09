from pathlib import Path

from stui.elements import ButtonElement, SliderElement, TitleElement, WriteElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_script_execution_collects_elements_in_order(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.title("Demo")
x = st.slider("x", 0, 10, 5)
if st.button("Run"):
    st.write("clicked")
st.write("x =", x)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], TitleElement)
    assert isinstance(elements[1], SliderElement)
    assert isinstance(elements[2], ButtonElement)
    assert isinstance(elements[3], WriteElement)
    assert elements[3].text == "x = 5"


def test_rerun_preserves_session_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0
st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.session_state.count = 9
    runtime.run_script()

    assert runtime.session_state.count == 9


def test_script_directory_is_on_sys_path_for_local_imports(tmp_path: Path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("VALUE = 42\n", encoding="utf-8")
    script = write_script(
        tmp_path,
        """
import stui as st
from helper import VALUE

st.write("value =", VALUE)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], WriteElement)
    assert elements[0].text == "value = 42"


def test_script_exception_renders_error_element(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
raise RuntimeError("boom")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert "RuntimeError: boom" in elements[0].traceback
