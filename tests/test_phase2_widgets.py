from pathlib import Path

from stui.elements import CheckboxElement, TextInputElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def widget_elements(runtime: Runtime) -> list[TextInputElement | CheckboxElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, (TextInputElement, CheckboxElement))
    ]


def test_text_input_default_and_state_persistence(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

name = st.text_input("Name", value="Ada")
st.write("name =", name)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["text_input:Name:0"] == "Ada"
    assert widget_elements(runtime)[0].value == "Ada"

    runtime.set_widget_value("text_input:Name:0", "Grace")
    runtime.run_script()

    assert runtime.session_state["text_input:Name:0"] == "Grace"
    assert widget_elements(runtime)[0].value == "Grace"


def test_checkbox_default_and_toggle_behavior(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

enabled = st.checkbox("Enable feature")
st.write("enabled =", enabled)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert runtime.session_state["checkbox:Enable feature:0"] is False
    assert widget_elements(runtime)[0].value is False

    runtime.set_widget_value("checkbox:Enable feature:0", True)
    runtime.run_script()

    assert runtime.session_state["checkbox:Enable feature:0"] is True
    assert widget_elements(runtime)[0].value is True


def test_generated_keys_for_new_widgets_are_stable(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.text_input("Name")
st.text_input("Name")
st.checkbox("Agree")
st.checkbox("Agree")
""",
    )
    runtime = Runtime(script)

    first = runtime.run_script()
    second = runtime.run_script()

    first_keys = [
        element.key
        for element in first
        if isinstance(element, (TextInputElement, CheckboxElement))
    ]
    second_keys = [
        element.key
        for element in second
        if isinstance(element, (TextInputElement, CheckboxElement))
    ]
    assert first_keys == [
        "text_input:Name:0",
        "text_input:Name:1",
        "checkbox:Agree:0",
        "checkbox:Agree:1",
    ]
    assert second_keys == first_keys


def test_explicit_keys_override_generated_keys_for_new_widgets(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.text_input("Name", key="custom-name")
st.checkbox("Agree", key="custom-agree")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    keys = [
        element.key
        for element in elements
        if isinstance(element, (TextInputElement, CheckboxElement))
    ]
    assert keys == ["custom-name", "custom-agree"]
