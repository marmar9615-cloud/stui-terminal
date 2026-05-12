from pathlib import Path

from stui.elements import (
    AlertElement,
    CaptionElement,
    CodeElement,
    DividerElement,
    ExceptionElement,
    HeaderElement,
    HelpElement,
    JsonElement,
    MarkdownElement,
    ProgressElement,
    SpinnerElement,
    StatusElement,
    SubheaderElement,
    TextElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_text_elements_render_in_order(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.header("Overview")
st.text("Plain text")
st.markdown("**markdown**")
st.divider()
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        HeaderElement,
        TextElement,
        MarkdownElement,
        DividerElement,
    ]
    assert elements[0].body == "Overview"
    assert elements[1].body == "Plain text"
    assert elements[2].body == "**markdown**"


def test_alerts_render_elements_with_kind_and_body(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.info("Heads up")
st.success("Saved")
st.warning("Careful")
st.error("Failed")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert all(isinstance(element, AlertElement) for element in elements)
    assert [(element.kind, element.body) for element in elements] == [
        ("info", "Heads up"),
        ("success", "Saved"),
        ("warning", "Careful"),
        ("error", "Failed"),
    ]


def test_display_api_elements_render_in_order_with_content(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.subheader("Details")
st.caption("small note")
st.code("print('hi')", language="python")
st.json({"b": 2, "a": [1]})
try:
    raise ValueError("bad input")
except ValueError as exc:
    st.exception(exc)
st.progress(0.5, text="Halfway")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        SubheaderElement,
        CaptionElement,
        CodeElement,
        JsonElement,
        ExceptionElement,
        ProgressElement,
    ]
    assert elements[0].body == "Details"
    assert elements[1].body == "small note"
    assert elements[2].body == "print('hi')"
    assert elements[2].language == "python"
    assert elements[3].text == '{\n  "a": [\n    1\n  ],\n  "b": 2\n}'
    assert "ValueError: bad input" in elements[4].traceback
    assert elements[5].value == 50
    assert elements[5].text == "Halfway"


def test_progress_normalizes_fraction_percent_and_bounds(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.progress(0)
st.progress(0.125)
st.progress(42)
st.progress(-10)
st.progress(500)
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [element.value for element in elements] == [0, 12, 42, 0, 100]


def test_status_spinner_and_help_elements_render_content(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

def train(epochs: int = 1) -> None:
    """Run a tiny training job."""

with st.status("Training", state="running", expanded=True):
    st.write("epoch 1")

with st.spinner("Loading"):
    st.caption("checkpoint")

st.help(train)
st.help("plain help text")
''',
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        StatusElement,
        SpinnerElement,
        HelpElement,
        HelpElement,
    ]
    status = elements[0]
    assert status.label == "Training"
    assert status.state == "running"
    assert status.expanded is True
    assert status.children is not None
    assert status.children[0].text == "epoch 1"
    spinner = elements[1]
    assert spinner.text == "Loading"
    assert spinner.children is not None
    assert spinner.children[0].body == "checkpoint"
    assert "train(epochs: int = 1) -> None" in elements[2].body
    assert "Run a tiny training job." in elements[2].body
    assert elements[3].body == "plain help text"


def test_status_rejects_unknown_state(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.status("Bad", state="pending")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert "st.status state must be one of" in elements[0].traceback
