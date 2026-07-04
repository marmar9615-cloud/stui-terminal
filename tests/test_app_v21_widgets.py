import asyncio
from pathlib import Path

from stui.app import StuiApp, script_signature
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_textual_app_multiselect_keyboard_smoke(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

tags = st.multiselect("Tags", ["alpha", "beta", "gamma"], default=["beta"])
st.write("tags =", tags)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["multiselect:Tags:0"] == ("beta",)

            await pilot.press("tab")
            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["multiselect:Tags:0"] == ("alpha", "beta")

            await pilot.press("down", "down", "space")
            await pilot.pause()
            assert runtime.session_state["multiselect:Tags:0"] == (
                "alpha",
                "beta",
                "gamma",
            )

            # The cursor survives the rerun, so a second space toggles the
            # same option off instead of jumping back to the first option.
            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["multiselect:Tags:0"] == ("alpha", "beta")

    asyncio.run(scenario())


def test_textual_app_toggle_switch_smoke(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

dark = st.toggle("Dark mode")
st.write("dark =", dark)
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert runtime.session_state["toggle:Dark mode:0"] is False

            await pilot.press("tab")
            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["toggle:Dark mode:0"] is True

            await pilot.press("space")
            await pilot.pause()
            assert runtime.session_state["toggle:Dark mode:0"] is False

    asyncio.run(scenario())


def test_textual_app_shows_toasts_once(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        """
import stui as st

if st.button("Notify"):
    st.toast("saved")
st.write("done")
""",
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)
        notified: list[str] = []
        app.notify = lambda message, **kwargs: notified.append(message)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert notified == []

            await pilot.press("tab")
            await pilot.press("enter")
            await pilot.pause()
            assert notified == ["saved"]
            assert runtime.toasts == []

            await pilot.press("r")
            await pilot.pause()
            assert notified == ["saved"]

    asyncio.run(scenario())


def test_script_signature_tracks_file_changes(tmp_path: Path) -> None:
    missing = tmp_path / "missing.py"
    assert script_signature(missing) is None

    script = write_script(tmp_path, "import stui as st\nst.title('One')\n")
    first = script_signature(script)
    assert first is not None

    script.write_text("import stui as st\nst.title('Two!')\n", encoding="utf-8")
    second = script_signature(script)
    assert second is not None
    assert second != first


def test_textual_app_watch_mode_reloads_script(tmp_path: Path) -> None:
    script = write_script(tmp_path, "import stui as st\nst.title('One')\n")

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime, watch=True)
        notified: list[str] = []
        app.notify = lambda message, **kwargs: notified.append(message)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.sub_title == "app.py · watching"
            assert runtime.elements[0].body == "One"

            await app._poll_script_change()
            await pilot.pause()
            assert runtime.elements[0].body == "One"
            assert notified == []

            script.write_text(
                "import stui as st\nst.title('Two')\n",
                encoding="utf-8",
            )
            await app._poll_script_change()
            await pilot.pause()
            assert runtime.elements[0].body == "Two"
            assert notified == ["Reloaded app.py"]

    asyncio.run(scenario())


def test_textual_app_without_watch_keeps_plain_subtitle(tmp_path: Path) -> None:
    script = write_script(tmp_path, "import stui as st\nst.title('One')\n")

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.sub_title == "app.py"

    asyncio.run(scenario())
