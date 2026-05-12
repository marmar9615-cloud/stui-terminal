from pathlib import Path

from stui.elements import ButtonElement, ErrorElement, TextInputElement, WriteElement
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
st.write(
    "state =",
    st.session_state.get("name", "missing"),
    st.session_state.get("epochs", "missing"),
)
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Ada",
        "epochs = 10",
        "state = missing missing",
    ]

    runtime.set_widget_value("name", "Grace")
    runtime.set_widget_value("epochs", 12)
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "epochs = 12",
        "state = missing missing",
    ]
    assert "name" not in runtime.session_state
    assert "epochs" not in runtime.session_state

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


def test_form_widget_callbacks_run_after_submit_commit(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(key):
    st.session_state.events.append(f"{key}:{st.session_state[key]}")

with st.form("profile"):
    name = st.text_input(
        "Name",
        value="Ada",
        key="name",
        on_change=record,
        args=("name",),
    )
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("name =", name)
st.write("events =", ",".join(st.session_state.events))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("name", "Grace")
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "events = ",
    ]

    runtime.press_button("form_submit_button:profile:Save:0")
    runtime.run_script()

    assert rendered_texts(runtime) == [
        "submitted = True",
        "name = Grace",
        "events = name:Grace",
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
    name = st.text_input("Name", value="Ada", key="name")
    submitted = st.form_submit_button(
        "Run",
        disabled=True,
        on_click=increment,
    )

st.write("submitted =", submitted)
st.write("name =", name)
st.write("state =", st.session_state.get("name", "missing"))
st.write("count =", st.session_state.count)
""",
    )
    runtime = Runtime(script)

    runtime.set_widget_value("name", "Grace")
    runtime.press_button("form_submit_button:disabled:Run:0")
    elements = runtime.run_script()

    buttons = [element for element in elements if isinstance(element, ButtonElement)]
    assert buttons[0].disabled is True
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "state = missing",
        "count = 0",
    ]
    assert "name" not in runtime.session_state


def test_disabled_form_widget_ignores_pending_change(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("disabled-widget"):
    name = st.text_input("Name", value="Ada", key="name", disabled=True)
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("name =", name)
st.write("state =", st.session_state.get("name", "missing"))
""",
    )
    runtime = Runtime(script)

    runtime.set_widget_value("name", "Grace")
    runtime.press_button("form_submit_button:disabled-widget:Save:0")
    runtime.run_script()

    assert rendered_texts(runtime) == [
        "submitted = True",
        "name = Ada",
        "state = missing",
    ]
    assert "name" not in runtime.session_state


def test_nested_form_renders_readable_error(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("outer"):
    with st.form("inner"):
        st.text_input("Name")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert elements[0].traceback == "Nested st.form blocks are not supported."


def test_form_submit_button_outside_form_renders_readable_error(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.form_submit_button("Save")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert (
        elements[0].traceback
        == "st.form_submit_button must be used inside st.form(...)."
    )


def test_explicit_form_widget_key_commits_only_on_submit(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.form("profile"):
    name = st.text_input("Name", value="Ada", key="person_name")
    submitted = st.form_submit_button("Save")

st.write("submitted =", submitted)
st.write("name =", name)
st.write("state =", st.session_state.get("person_name", "missing"))
""",
    )
    runtime = Runtime(script)

    runtime.run_script()
    elements = runtime.run_script()
    text_inputs = [
        element for element in elements if isinstance(element, TextInputElement)
    ]
    assert text_inputs[0].key == "person_name"

    runtime.set_widget_value("person_name", "Grace")
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = False",
        "name = Grace",
        "state = missing",
    ]

    runtime.press_button("form_submit_button:profile:Save:0")
    runtime.run_script()
    assert rendered_texts(runtime) == [
        "submitted = True",
        "name = Grace",
        "state = Grace",
    ]
