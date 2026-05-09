from __future__ import annotations

from pathlib import Path

import pytest

from stui.elements import (
    ButtonElement,
    CheckboxElement,
    SliderElement,
    TextInputElement,
)
from stui.runtime import Runtime
from stui.widgets.slider import StuiSlider, snap_value


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_disabled_button_ignores_pending_runtime_press(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if st.button("Run", disabled=True):
    st.write("clicked")
st.write("done")
""",
    )
    runtime = Runtime(script)

    runtime.press_button("button:Run:0")
    elements = runtime.run_script()

    assert isinstance(elements[0], ButtonElement)
    assert elements[0].disabled is True
    assert [getattr(element, "text", None) for element in elements] == [None, "done"]


def test_disabled_non_button_widgets_emit_disabled_elements(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.slider("Amount", 0, 10, 5, disabled=True)
st.text_input("Name", value="Ada", disabled=True)
st.checkbox("Enabled", value=True, disabled=True)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], SliderElement)
    assert elements[0].disabled is True
    assert elements[0].value == 5
    assert isinstance(elements[1], TextInputElement)
    assert elements[1].disabled is True
    assert elements[1].value == "Ada"
    assert isinstance(elements[2], CheckboxElement)
    assert elements[2].disabled is True
    assert elements[2].value is True


def test_disabled_slider_widget_actions_do_not_commit_or_post_message() -> None:
    slider = StuiSlider(
        label="Amount",
        key="slider:Amount:0",
        min_value=0,
        max_value=10,
        value=5,
        step=1,
        disabled=True,
    )
    posted_messages: list[object] = []
    slider.post_message = posted_messages.append  # type: ignore[method-assign]

    slider.action_increase()
    slider.action_decrease()
    slider.action_minimum()
    slider.action_maximum()

    assert slider.value == 5
    assert posted_messages == []


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-100, -10),
        (-9, -8),
        (-7, -6),
        (99, 10),
    ],
)
def test_snap_value_clamps_before_snapping_int_values(
    value: int,
    expected: int,
) -> None:
    snapped = snap_value(value, -10, 10, 2)

    assert snapped == expected
    assert isinstance(snapped, int)


def test_snap_value_snaps_float_values_without_binary_precision_drift() -> None:
    value = 0.0
    for _ in range(7):
        value = snap_value(value + 0.1, 0.0, 1.0, 0.1)

    assert value == 0.7
    assert repr(value) == "0.7"


def test_snap_value_clamps_float_values_to_exact_bounds() -> None:
    assert snap_value(-0.000000001, 0.0, 1.0, 0.1) == 0.0
    assert snap_value(1.000000001, 0.0, 1.0, 0.1) == 1.0


def test_snap_value_raises_when_max_is_less_than_min() -> None:
    with pytest.raises(ValueError, match="max_value"):
        snap_value(5, 10, 0, 1)
