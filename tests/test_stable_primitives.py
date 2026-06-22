import asyncio
from pathlib import Path

import stui as st
from stui.app import StuiApp
from stui.elements import (
    ErrorElement,
    HelpElement,
    SpinnerElement,
    StatusElement,
    TextElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_status_spinner_and_help_render_simple_elements(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

def sample(value: int) -> str:
    """Return the rendered value."""
    return str(value)

st.status("Indexing", state="complete")
with st.status("Building", state="running", expanded=True):
    st.text("step 1")
with st.spinner("Working"):
    st.text("inside spinner")
st.help(sample)
st.help("plain help text")
''',
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert isinstance(elements[0], StatusElement)
    assert elements[0].label == "Indexing"
    assert elements[0].state == "complete"
    assert elements[0].expanded is False

    assert isinstance(elements[1], StatusElement)
    assert elements[1].label == "Building"
    assert elements[1].state == "running"
    assert elements[1].expanded is True
    assert elements[1].children is not None
    assert [type(child) for child in elements[1].children] == [TextElement]
    assert elements[1].children[0].body == "step 1"

    assert isinstance(elements[2], SpinnerElement)
    assert elements[2].text == "Working"
    assert elements[2].children is not None
    assert [type(child) for child in elements[2].children] == [TextElement]
    assert elements[2].children[0].body == "inside spinner"

    assert isinstance(elements[3], HelpElement)
    assert "sample(value: int) -> str" in elements[3].body
    assert "Return the rendered value." in elements[3].body

    assert isinstance(elements[4], HelpElement)
    assert elements[4].body == "plain help text"


def test_status_context_defaults_to_collapsed_but_keeps_children(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.status("Collapsed details"):
    st.text("hidden until expanded")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [StatusElement]
    status = elements[0]
    assert status.expanded is False
    assert status.children is not None
    assert [type(child) for child in status.children] == [TextElement]
    assert status.children[0].body == "hidden until expanded"


def test_status_accepts_all_documented_states(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.status("Running", state="running")
st.status("Complete", state="complete")
st.status("Error", state="error")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [element.state for element in elements] == [
        "running",
        "complete",
        "error",
    ]


def test_spinner_default_text_and_nested_status_children(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.spinner():
    with st.status("Nested", expanded=True):
        st.text("child")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [SpinnerElement]
    spinner = elements[0]
    assert spinner.text == "Working..."
    assert spinner.children is not None
    assert [type(child) for child in spinner.children] == [StatusElement]
    nested_status = spinner.children[0]
    assert nested_status.children is not None
    assert [type(child) for child in nested_status.children] == [TextElement]


def test_help_formats_stui_public_function_and_fallback_object(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

class PlainObject:
    pass

st.help(st.progress)
st.help(PlainObject())
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [HelpElement, HelpElement]
    assert "progress(" in elements[0].body
    assert "value:" in elements[0].body
    assert "PlainObject object at" in elements[1].body


def test_status_rejects_unknown_state_without_traceback(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.status("bad", state="pending")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [ErrorElement]
    assert "state must be one of" in elements[0].traceback


def test_textual_app_renders_stable_primitive_blocks(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.status("Done", state="complete")
with st.spinner("Working"):
    st.text("child")
st.help("help text")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-status-complete"))) == 1
            assert len(list(app.query(".stui-spinner"))) >= 1
            assert len(list(app.query(".stui-help"))) == 1

    asyncio.run(scenario())


def test_high_contrast_panel_styles_are_theme_aware(tmp_path: Path) -> None:
    script = write_script(tmp_path, "import stui as st\nst.write('ok')\n")
    app = StuiApp(Runtime(script))
    app.stui_theme = "high-contrast"

    assert app._status_style("running") == "#ffff00"
    assert app._status_style("complete") == "#ffffff"
    assert app._alert_style("warning") == "#ffff00"
    assert app._panel_style("help") == "#ffff00"
    assert app._panel_style("error") == "#ffffff"
    assert app._traceback_text_style() == "#ffffff"


def test_help_public_function_probe_is_real() -> None:
    # Keep this public-object probe grounded in the imported package API.
    assert callable(st.progress)
