from pathlib import Path

from stui.elements import (
    AlertElement,
    DividerElement,
    HeaderElement,
    MarkdownElement,
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
