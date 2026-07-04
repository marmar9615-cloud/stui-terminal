from pathlib import Path

from stui.elements import ErrorElement, ToggleElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def toggle_elements(runtime: Runtime) -> list[ToggleElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, ToggleElement)
    ]


def test_toggle_default_and_flip_behavior(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

dark = st.toggle("Dark mode")
st.write("dark =", dark)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["toggle:Dark mode:0"] is False
    assert toggle_elements(runtime)[0].value is False

    runtime.set_widget_value("toggle:Dark mode:0", True)
    runtime.run_script()

    assert runtime.session_state["toggle:Dark mode:0"] is True
    assert toggle_elements(runtime)[0].value is True


def test_toggle_default_true_and_disabled(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

locked = st.toggle("Locked", value=True, disabled=True)
st.write("locked =", locked)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("toggle:Locked:0", False)
    runtime.run_script()

    assert runtime.session_state["toggle:Locked:0"] is True
    assert toggle_elements(runtime)[0].disabled is True


def test_toggle_on_change_fires_only_on_change(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "calls" not in st.session_state:
    st.session_state.calls = 0

def bump():
    st.session_state.calls += 1

dark = st.toggle("Dark mode", on_change=bump)
st.write(dark)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state.calls == 0

    runtime.set_widget_value("toggle:Dark mode:0", True)
    runtime.run_script()
    assert runtime.session_state.calls == 1

    runtime.run_script()
    assert runtime.session_state.calls == 1


def test_toast_collects_messages_for_the_current_run(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.title("App")
st.toast("first")
st.toast(41 + 1)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.toasts == ["first", "42"]

    runtime.run_script()
    assert runtime.toasts == ["first", "42"]


def test_toast_only_fires_on_the_run_that_queued_it(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if st.button("Notify"):
    st.toast("pressed")
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.toasts == []

    runtime.press_button("button:Notify:0")
    runtime.run_script()
    assert runtime.toasts == ["pressed"]

    runtime.run_script()
    assert runtime.toasts == []


def test_toast_is_cleared_when_the_script_errors(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.toast("about to fail")
raise ValueError("boom")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], ErrorElement)
    assert runtime.toasts == []
