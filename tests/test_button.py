from pathlib import Path

from stui.elements import WriteElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def rendered_texts(runtime: Runtime) -> list[str]:
    return [
        element.text
        for element in runtime.elements
        if isinstance(element, WriteElement)
    ]


def test_button_returns_true_once_then_false(tmp_path: Path) -> None:
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
    assert rendered_texts(runtime) == ["count = 0"]

    runtime.press_button("button:Increment:0")
    runtime.run_script()
    assert runtime.session_state.count == 1
    assert rendered_texts(runtime) == ["count = 1"]

    runtime.run_script()
    assert runtime.session_state.count == 1
    assert rendered_texts(runtime) == ["count = 1"]
