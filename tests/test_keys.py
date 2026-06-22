from pathlib import Path

import pytest

from stui.elements import ButtonElement, ErrorElement, SliderElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_generated_widget_keys_are_stable(tmp_path: Path) -> None:
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

    first = runtime.run_script()
    second = runtime.run_script()

    first_keys = [
        element.key
        for element in first
        if isinstance(element, (SliderElement, ButtonElement))
    ]
    second_keys = [
        element.key
        for element in second
        if isinstance(element, (SliderElement, ButtonElement))
    ]
    assert first_keys == ["slider:x:0", "slider:x:1", "button:Go:0"]
    assert second_keys == first_keys


def test_explicit_keys_override_generated_keys(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.slider("x", key="custom-x")
st.button("Go", key="custom-go")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    keys = [
        element.key
        for element in elements
        if isinstance(element, (SliderElement, ButtonElement))
    ]
    assert keys == ["custom-x", "custom-go"]


def test_duplicate_explicit_keys_across_widget_types_render_error(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.button("Go", key="shared")
st.text_input("Name", key="shared")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert 'Duplicate widget key "shared"' in elements[0].traceback


@pytest.mark.parametrize(
    "body",
    [
        """
import stui as st

st.slider("x")
st.text_input("Name", key="slider:x:0")
""",
        """
import stui as st

st.text_input("Name", key="slider:x:0")
st.slider("x")
""",
    ],
)
def test_generated_and_explicit_key_collisions_render_error(
    tmp_path: Path,
    body: str,
) -> None:
    script = write_script(tmp_path, body)
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert 'Duplicate widget key "slider:x:0"' in elements[0].traceback
