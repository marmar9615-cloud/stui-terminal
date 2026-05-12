from pathlib import Path

from stui.elements import ButtonElement, WriteElement
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


def test_form_submit_button_returns_true_once_and_preserves_widget_state(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("settings"):
    name = st.text_input("Name", value="Ada", key="name")
    epochs = st.number_input(
        "Epochs",
        min_value=1,
        max_value=100,
        value=10,
        key="epochs",
    )
    submitted = st.form_submit_button("Run")

st.write("submitted =", submitted)
st.write("name =", name)
st.write("epochs =", epochs)
st.write("state =", st.session_state.name, st.session_state.epochs)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Ada",
        "epochs = 10",
        "state = Ada 10",
    ]

    runtime.set_widget_value("name", "Grace")
    runtime.set_widget_value("epochs", 12)
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "epochs = 12",
        "state = Grace 12",
    ]

    runtime.press_button("form_submit_button:settings:Run:0")
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = True",
        "name = Grace",
        "epochs = 12",
        "state = Grace 12",
    ]

    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "epochs = 12",
        "state = Grace 12",
    ]


def test_form_submit_button_callback_receives_args_kwargs(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(source, *, suffix):
    st.session_state.events.append(f"{source}:{suffix}")

with st.form("actions"):
    submitted = st.form_submit_button(
        "Save",
        on_click=record,
        args=("form",),
        kwargs={"suffix": "submitted"},
    )

st.write("submitted =", submitted)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == ["submitted = False", "events = "]

    runtime.press_button("form_submit_button:actions:Save:0")
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = True",
        "events = form:submitted",
    ]

    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "events = form:submitted",
    ]


def test_disabled_form_submit_button_ignores_pending_press(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0

def increment():
    st.session_state.count += 1

with st.form("disabled"):
    submitted = st.form_submit_button(
        "Run",
        disabled=True,
        on_click=increment,
    )

st.write("submitted =", submitted)
st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    runtime.press_button("form_submit_button:disabled:Run:0")
    elements = runtime.run_script()

    assert isinstance(elements[0], ButtonElement)
    assert elements[0].disabled is True
    assert rendered_texts(runtime) == ["submitted = False", "count = 0"]

