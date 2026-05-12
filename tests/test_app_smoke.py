import asyncio
from pathlib import Path

from stui.app import StuiApp, dom_id_for_key
from stui.elements import ProgressElement
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


def test_textual_app_display_api_smoke(tmp_path) -> None:
    script = tmp_path / "display_app.py"
    script.write_text(
        """
import stui as st

st.subheader("Details")
st.caption("small note")
st.code("print('hi')", language="python")
st.json({"ok": True})
try:
    raise RuntimeError("boom")
except RuntimeError as exc:
    st.exception(exc)
st.progress(75, text="Almost")
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(runtime.elements[-1], ProgressElement)
            assert runtime.elements[-1].value == 75

    asyncio.run(scenario())


def test_textual_app_new_widgets_smoke(tmp_path) -> None:
    script = tmp_path / "new_widgets_app.py"
    script.write_text(
        """
import stui as st

st.number_input("Count", value=2, key="count")
st.selectbox("Model", ["tiny", "base"], key="model")
st.radio("Mode", ["fast", "careful"], key="mode")
st.table([{"name": "Ada", "score": 10}])
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["count"] == 2
            assert runtime.session_state["model"] == "tiny"
            assert runtime.session_state["mode"] == "fast"

            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "count"

            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "model"
            await pilot.press("right")
            await pilot.pause()
            assert runtime.session_state["model"] == "base"
            assert runtime.last_focused_key == "model"
            assert getattr(app.focused, "stui_key", None) == "model"

            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "mode"

            await pilot.press("shift+tab")
            assert getattr(app.focused, "stui_key", None) == "model"

    asyncio.run(scenario())


def test_textual_app_button_enter_and_space_activation(tmp_path) -> None:
    script = tmp_path / "button_keys_app.py"
    script.write_text(
        """
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Go", key="go"):
    st.session_state.count += 1

with st.form("actions"):
    submitted = st.form_submit_button("Save")

if submitted:
    st.session_state.count += 10

st.write("count =", st.session_state.count)
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("tab")
            assert getattr(app.focused, "stui_key", None) == "go"

            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state.count == 1
            assert runtime.last_focused_key == "go"
            assert getattr(app.focused, "stui_key", None) == "go"

            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state.count == 2

            await pilot.press("tab")
            assert (
                getattr(app.focused, "stui_key", None)
                == "form_submit_button:actions:Save:0"
            )

            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state.count == 12

            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state.count == 22

    asyncio.run(scenario())


def test_textual_app_focus_order_enters_column_contents(tmp_path) -> None:
    script = tmp_path / "column_focus_app.py"
    script.write_text(
        """
import stui as st

left, right = st.columns(2)
with left:
    st.button("Left", key="left")
    st.text_input("Name", key="name")
with right:
    st.checkbox("Right", key="right")
    st.slider("Amount", 0, 10, 5, key="amount")
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(120, 24)) as pilot:
            await pilot.pause()
            focused_keys = []
            for _ in range(4):
                await pilot.press("tab")
                await pilot.pause()
                focused_keys.append(getattr(app.focused, "stui_key", None))

            assert focused_keys == ["left", "name", "right", "amount"]

    asyncio.run(scenario())


def test_textual_app_documented_selection_and_slider_keys(tmp_path) -> None:
    script = tmp_path / "documented_keys_app.py"
    script.write_text(
        """
import stui as st

st.selectbox("Model", ["tiny", "base", "large"], index=1, key="model")
st.radio("Mode", ["fast", "careful"], key="mode")
st.slider("Amount", 0, 10, 5, key="amount")
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()

            app.set_focus(app.query_one(f"#{dom_id_for_key('model')}"))
            await pilot.pause()
            assert getattr(app.focused, "stui_key", None) == "model"
            await pilot.press("down")
            await pilot.pause()
            assert runtime.session_state["model"] == "large"
            await pilot.press("up")
            await pilot.pause()
            assert runtime.session_state["model"] == "base"
            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state["model"] == "large"
            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["model"] == "base"

            await pilot.press("tab")
            await pilot.pause()
            assert getattr(app.focused, "stui_key", None) == "mode"
            await pilot.press("right")
            await pilot.pause()
            assert runtime.session_state["mode"] == "careful"
            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["mode"] == "fast"
            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["mode"] == "careful"
            await pilot.press("enter")
            await pilot.pause()
            assert runtime.session_state["mode"] == "fast"

            app.set_focus(app.query_one(f"#{dom_id_for_key('amount')}"))
            await pilot.pause()
            assert getattr(app.focused, "stui_key", None) == "amount"
            await pilot.press("right")
            await pilot.pause()
            assert runtime.session_state["amount"] == 6
            app.set_focus(app.query_one(f"#{dom_id_for_key('amount')}"))
            await pilot.pause()
            await pilot.press("left")
            await pilot.pause()
            assert runtime.session_state["amount"] == 5
            await pilot.press("end")
            await pilot.pause()
            assert runtime.session_state["amount"] == 10
            app.set_focus(app.query_one(f"#{dom_id_for_key('amount')}"))
            await pilot.pause()
            await pilot.press("home")
            await pilot.pause()
            assert runtime.session_state["amount"] == 0

    asyncio.run(scenario())


def test_textual_app_q_quits_and_r_reruns(tmp_path) -> None:
    script = tmp_path / "app_keys_app.py"
    script.write_text(
        """
import stui as st

st.session_state.runs = st.session_state.get("runs", 0) + 1
st.write("runs =", st.session_state.runs)
""",
        encoding="utf-8",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state.runs == 1

            await pilot.press("r")
            await pilot.pause()
            assert runtime.session_state.runs == 2

            await pilot.press("q")
            await pilot.pause()
            assert app.is_running is False

    asyncio.run(scenario())
