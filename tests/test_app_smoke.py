import asyncio
from pathlib import Path

from stui.app import StuiApp
from stui.runtime import Runtime


def test_textual_app_slider_and_button_smoke() -> None:
    async def scenario() -> None:
        runtime = Runtime(Path("examples/basic.py"))
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["slider:x:0"] == 10
            assert runtime.session_state.count == 0

            await pilot.press("tab")
            await pilot.press("right")
            await pilot.pause()
            assert runtime.session_state["slider:x:0"] == 11
            assert runtime.last_focused_key == "slider:x:0"
            assert getattr(app.focused, "stui_key", None) == "slider:x:0"

            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state.count == 1

            await pilot.press("r")
            await pilot.pause()
            assert runtime.session_state.count == 1

    asyncio.run(scenario())


def test_textual_app_text_input_and_checkbox_smoke(tmp_path) -> None:
    script = tmp_path / "phase2_app.py"
    script.write_text(
        """
import stui as st

name = st.text_input("Name", value="Ada")
enabled = st.checkbox("Enabled")

st.write("name =", name)
st.write("enabled =", enabled)
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["text_input:Name:0"] == "Ada"
            assert runtime.session_state["checkbox:Enabled:0"] is False

            await pilot.press("tab")
            await pilot.press(" ", "L", "o", "v", "e", "l", "a", "c", "e")
            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state["text_input:Name:0"] == " Lovelace"
            assert runtime.last_focused_key == "text_input:Name:0"

            await pilot.press("tab")
            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["checkbox:Enabled:0"] is True
            assert runtime.last_focused_key == "checkbox:Enabled:0"

    asyncio.run(scenario())
