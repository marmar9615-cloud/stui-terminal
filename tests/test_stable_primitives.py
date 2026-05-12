import asyncio
from pathlib import Path

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
