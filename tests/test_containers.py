import asyncio
from pathlib import Path

from stui.app import StuiApp
from stui.elements import (
    ContainerElement,
    ExpanderElement,
    TextElement,
    WriteElement,
)
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_container_context_preserves_order_and_children(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

st.write("before")
with st.container():
    st.text("inside")
st.write("after")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert [type(element) for element in elements] == [
        WriteElement,
        ContainerElement,
        WriteElement,
    ]
    assert elements[0].text == "before"
    assert isinstance(elements[1].children[0], TextElement)
    assert elements[1].children[0].body == "inside"
    assert elements[2].text == "after"


def test_nested_container_and_expander_keep_nesting(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.container():
    st.write("outer")
    with st.expander("Details", expanded=True):
        st.write("inner")
    st.write("tail")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    container = elements[0]
    assert isinstance(container, ContainerElement)
    assert [type(element) for element in container.children] == [
        WriteElement,
        ExpanderElement,
        WriteElement,
    ]
    expander = container.children[1]
    assert isinstance(expander, ExpanderElement)
    assert expander.label == "Details"
    assert expander.expanded is True
    assert expander.children is not None
    assert isinstance(expander.children[0], WriteElement)
    assert expander.children[0].text == "inner"


def test_expander_defaults_to_static_closed(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Closed"):
    st.write("hidden for now")
""",
    )
    runtime = Runtime(script)

    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ExpanderElement)
    assert elements[0].label == "Closed"
    assert elements[0].expanded is False
    assert elements[0].children is not None
    assert isinstance(elements[0].children[0], WriteElement)


def test_container_context_stack_unwinds_after_script_error(tmp_path: Path) -> None:
    failing = write_script(
        tmp_path,
        """
import stui as st

with st.container():
    raise RuntimeError("boom")
""",
    )
    succeeding = write_script(
        tmp_path,
        """
import stui as st

st.write("ok")
""",
    )
    runtime = Runtime(failing)
    runtime.run_script()

    runtime.script_path = succeeding
    elements = runtime.run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], WriteElement)
    assert elements[0].text == "ok"


def test_static_expanders_render_open_and_closed(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

with st.expander("Closed"):
    st.write("closed child")
with st.expander("Open", expanded=True):
    st.write("open child")
""",
    )
    runtime = Runtime(script)
    app = StuiApp(runtime)

    async def scenario() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(list(app.query(".stui-expander"))) == 2
            assert len(list(app.query(".write"))) == 1

    asyncio.run(scenario())
