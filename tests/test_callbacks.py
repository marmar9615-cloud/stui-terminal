from pathlib import Path

from stui.elements import ErrorElement, WriteElement
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


def test_button_on_click_receives_args_kwargs_and_is_one_shot(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(source, *, suffix):
    st.session_state.events.append(f"{source}:{suffix}")

pressed = st.button(
    "Save",
    on_click=record,
    args=("button",),
    kwargs={"suffix": "clicked"},
)
st.write("pressed =", pressed)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["pressed = False", "events = "]

    runtime.press_button("button:Save:0")
    runtime.run_script()
    assert rendered_texts(runtime) == ["pressed = True", "events = button:clicked"]

    runtime.run_script()
    assert rendered_texts(runtime) == ["pressed = False", "events = button:clicked"]


def test_slider_on_change_runs_after_state_update_with_args_kwargs(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

value = st.slider(
    "Amount",
    0,
    10,
    3,
    key="amount",
    on_change=record,
    args=("amount",),
    kwargs={"prefix": "slider"},
)
st.write("value =", value)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["value = 3", "events = "]

    runtime.set_widget_value("amount", 7)
    runtime.run_script()
    assert rendered_texts(runtime) == ["value = 7", "events = slider:7"]


def test_text_input_on_change_runs_after_state_update_with_args_kwargs(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

value = st.text_input(
    "Name",
    value="Ada",
    key="name",
    on_change=record,
    args=("name",),
    kwargs={"prefix": "text"},
)
st.write("value =", value)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["value = Ada", "events = "]

    runtime.set_widget_value("name", "Grace")
    runtime.run_script()
    assert rendered_texts(runtime) == ["value = Grace", "events = text:Grace"]


def test_checkbox_on_change_runs_after_state_update_with_args_kwargs(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(key, *, prefix):
    st.session_state.events.append(f"{prefix}:{st.session_state[key]}")

value = st.checkbox(
    "Enabled",
    value=False,
    key="enabled",
    on_change=record,
    args=("enabled",),
    kwargs={"prefix": "checkbox"},
)
st.write("value =", value)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["value = False", "events = "]

    runtime.set_widget_value("enabled", True)
    runtime.run_script()
    assert rendered_texts(runtime) == ["value = True", "events = checkbox:True"]


def test_callback_state_changes_roll_back_when_script_crashes(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append("clicked")

pressed = st.button("Crash", on_click=record)
if pressed:
    raise RuntimeError("after callback")

st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["events = "]

    runtime.press_button("button:Crash:0")
    elements = runtime.run_script()
    assert [type(element) for element in elements] == [ErrorElement]
    assert runtime.session_state.events == []

    runtime.run_script()
    assert rendered_texts(runtime) == ["events = "]
