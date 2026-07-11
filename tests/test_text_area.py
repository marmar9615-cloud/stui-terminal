import asyncio
from pathlib import Path

from stui.app import StuiApp, StuiTextArea
from stui.elements import ErrorElement, TextAreaElement, WriteElement
from stui.runtime import Runtime


def write_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "app.py"
    script.write_text(body, encoding="utf-8")
    return script


def text_area_elements(runtime: Runtime) -> list[TextAreaElement]:
    return [
        element
        for element in runtime.elements
        if isinstance(element, TextAreaElement)
    ]


def rendered_texts(runtime: Runtime) -> list[str]:
    return [
        element.text
        for element in runtime.elements
        if isinstance(element, WriteElement)
    ]


def test_text_area_defaults_multiline_unicode_and_keys(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

first = st.text_area("Prompt", value="first\\nsecond λ")
second = st.text_area(
    "Prompt",
    key="notes",
    height=8,
    placeholder="Write notes",
    max_chars=40,
)
st.write(first)
st.write(second)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    assert runtime.session_state["text_area:Prompt:0"] == "first\nsecond λ"
    assert runtime.session_state["notes"] == ""
    assert text_area_elements(runtime) == [
        TextAreaElement(
            label="Prompt",
            key="text_area:Prompt:0",
            value="first\nsecond λ",
        ),
        TextAreaElement(
            label="Prompt",
            key="notes",
            value="",
            height=8,
            placeholder="Write notes",
            max_chars=40,
        ),
    ]


def test_text_area_neutralizes_terminal_controls_in_value_and_metadata(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        r'''
import stui as st

value = st.text_area(
    "Prompt\x1b[2J",
    value="safe\n\tλ\x1b]52;c;Y2xlYXI=\x1b\\\x9b2J\x7f",
    key="prompt",
    placeholder="Paste\x07 here",
)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()

    expected = "safe\n\tλ\\x1b]52;c;Y2xlYXI=\\x1b\\\\x9b2J\\x7f"
    element = text_area_elements(runtime)[0]
    assert runtime.session_state["prompt"] == expected
    assert rendered_texts(runtime) == [expected]
    assert element.value == expected
    assert element.label == "Prompt\\x1b[2J"
    assert element.placeholder == "Paste\\x07 here"
    assert "\x1b" not in element.value
    assert "\x9b" not in element.value
    assert "\x7f" not in element.value


def test_text_area_neutralizes_queued_controls_before_callback_and_form_commit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append(st.session_state["prompt"])

with st.form("editor"):
    value = st.text_area("Prompt", key="prompt", on_change=record)
    submitted = st.form_submit_button("Save")

st.write(value)
st.write(submitted)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "line\n\x1b[2J\x9b0m")
    runtime.run_script()

    assert "prompt" not in runtime.session_state
    assert text_area_elements(runtime)[0].value == "line\n\\x1b[2J\\x9b0m"

    runtime.press_button("form_submit_button:editor:Save:0")
    runtime.run_script()

    assert runtime.session_state["prompt"] == "line\n\\x1b[2J\\x9b0m"
    assert runtime.session_state["events"] == ["line\n\\x1b[2J\\x9b0m"]


def test_text_area_compositor_does_not_emit_value_control_sequences(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        r'''
import stui as st

st.text_area(
    "External data",
    value="BEGIN\x1b]52;c;U1RVSS1JTkVSVA==\x1b\\\x1b[2J\x9b0mEND",
    key="external-data",
)
''',
    )

    async def scenario() -> None:
        app = StuiApp(Runtime(script))
        async with app.run_test(headless=True, size=(100, 32)) as pilot:
            await pilot.pause()
            update = app.screen._compositor.render_update(
                full=True,
                screen_stack=app.screen_stack,
            )
            assert update is not None
            frame = update.render_segments(app.console)

        assert "\x1b]52;c;U1RVSS1JTkVSVA==\x1b\\" not in frame
        assert "\x1b[2J" not in frame
        assert "\x9b0m" not in frame
        assert "\\x1b]52;c;U1RVSS1JTkVSVA=" in frame
        assert "\\x1b[2J\\x9b0mEND" in frame

    asyncio.run(scenario())


def test_text_area_live_replace_neutralizes_controls_before_render(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

st.text_area("External data", key="external-data")
''',
    )
    osc52 = "\x1b]52;c;U1RVSS1MSVZF\x1b\\"
    csi = "\x1b[2J"
    c1 = "\x9b0m"
    inserted = f"safe\n\tλ{osc52}{csi}{c1}END"
    visible = (
        "safe\n\tλ\\x1b]52;c;U1RVSS1MSVZF\\x1b\\"
        "\\x1b[2J\\x9b0mEND"
    )

    async def scenario() -> None:
        app = StuiApp(Runtime(script))
        async with app.run_test(headless=True, size=(100, 32)) as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            text_area.replace(inserted, (0, 0), (0, 0))
            await pilot.pause()

            update = app.screen._compositor.render_update(
                full=True,
                screen_stack=app.screen_stack,
            )
            assert update is not None
            frame = update.render_segments(app.console)

            assert text_area.text == visible
            assert osc52 not in text_area.text
            assert csi not in text_area.text
            assert c1 not in text_area.text
            assert osc52 not in frame
            assert csi not in frame
            assert c1 not in frame
            assert "\\x1b]52;c;U1RVSS1MSVZF" in frame
            assert "\\x1b[2J\\x9b0mEND" in frame

    asyncio.run(scenario())


def test_text_area_state_persistence_and_max_chars(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

value = st.text_area("Prompt", key="prompt", max_chars=5)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "abcdef")
    runtime.run_script()

    assert runtime.session_state["prompt"] == "abcde"
    assert text_area_elements(runtime)[0].value == "abcde"
    assert rendered_texts(runtime) == ["abcde"]

    runtime.run_script()
    assert runtime.session_state["prompt"] == "abcde"


def test_text_area_max_chars_normalizes_before_commit_and_noop_rerun(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append(st.session_state["prompt"])

value = st.text_area(
    "Prompt",
    key="prompt",
    max_chars=7,
    on_change=record,
)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "A\x1bBλC")
    runtime.run_script()

    expected = "A\\x1bBλ"
    assert runtime.session_state["prompt"] == expected
    assert text_area_elements(runtime)[0].value == expected
    assert rendered_texts(runtime) == [expected]
    assert runtime.session_state["events"] == [expected]

    runtime.run_script()

    assert runtime.session_state["prompt"] == expected
    assert text_area_elements(runtime)[0].value == expected
    assert rendered_texts(runtime) == [expected]
    assert runtime.session_state["events"] == [expected]


def test_text_area_rejects_invalid_height_and_max_chars(tmp_path: Path) -> None:
    invalid_cases = [
        ("st.text_area('Prompt', height=True)", "height must be an integer"),
        ("st.text_area('Prompt', height=2)", "height must be an integer"),
        ("st.text_area('Prompt', max_chars=True)", "max_chars must be a positive"),
        ("st.text_area('Prompt', max_chars=0)", "max_chars must be a positive"),
    ]

    for index, (call, expected) in enumerate(invalid_cases):
        script = tmp_path / f"invalid_{index}.py"
        script.write_text(
            f"import stui as st\n{call}\n",
            encoding="utf-8",
        )
        elements = Runtime(script).run_script()
        assert len(elements) == 1
        assert isinstance(elements[0], ErrorElement)
        assert expected in elements[0].traceback


def test_text_area_duplicate_explicit_key_is_readable(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

st.text_area("First", key="prompt")
st.text_area("Second", key="prompt")
''',
    )

    elements = Runtime(script).run_script()

    assert len(elements) == 1
    assert isinstance(elements[0], ErrorElement)
    assert 'Duplicate widget key "prompt"' in elements[0].traceback


def test_text_area_disabled_ignores_changes(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

value = st.text_area("Prompt", value="locked", key="prompt", disabled=True)
st.write(value)
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "changed")
    runtime.run_script()

    assert runtime.session_state["prompt"] == "locked"
    assert text_area_elements(runtime)[0].disabled is True
    assert rendered_texts(runtime) == ["locked"]


def test_text_area_callback_runs_after_state_update_with_args_kwargs(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record(prefix, *, suffix):
    st.session_state.events.append(
        f"{prefix}:{st.session_state['prompt']}:{suffix}"
    )

value = st.text_area(
    "Prompt",
    key="prompt",
    on_change=record,
    args=("changed",),
    kwargs={"suffix": "done"},
)
st.write(value)
st.write("|".join(st.session_state.events))
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "line one\nline two")
    runtime.run_script()

    assert runtime.session_state["prompt"] == "line one\nline two"
    assert runtime.session_state["events"] == [
        "changed:line one\nline two:done"
    ]

    runtime.run_script()
    assert len(runtime.session_state["events"]) == 1


def test_text_area_form_value_and_callback_commit_on_submit(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

if "events" not in st.session_state:
    st.session_state.events = []

def record():
    st.session_state.events.append(st.session_state["prompt"])

with st.form("editor"):
    value = st.text_area("Prompt", value="draft", key="prompt", on_change=record)
    submitted = st.form_submit_button("Save")

st.write(submitted)
st.write(value)
st.write(st.session_state.get("prompt", "missing"))
st.write("|".join(st.session_state.events))
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "line one\nline two")
    runtime.run_script()

    assert "prompt" not in runtime.session_state
    assert runtime.session_state["events"] == []
    assert rendered_texts(runtime) == [
        "False",
        "line one\nline two",
        "missing",
        "",
    ]

    runtime.press_button("form_submit_button:editor:Save:0")
    runtime.run_script()

    assert runtime.session_state["prompt"] == "line one\nline two"
    assert runtime.session_state["events"] == ["line one\nline two"]
    assert rendered_texts(runtime) == [
        "True",
        "line one\nline two",
        "line one\nline two",
        "line one\nline two",
    ]


def test_text_area_form_disabled_change_is_not_committed(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

with st.form("editor"):
    value = st.text_area(
        "Prompt",
        value="locked",
        key="prompt",
        disabled=True,
    )
    submitted = st.form_submit_button("Save")

st.write(submitted)
st.write(value)
st.write(st.session_state.get("prompt", "missing"))
''',
    )
    runtime = Runtime(script)

    runtime.run_script()
    runtime.set_widget_value("prompt", "changed")
    runtime.run_script()
    runtime.press_button("form_submit_button:editor:Save:0")
    runtime.run_script()

    assert "prompt" not in runtime.session_state
    assert rendered_texts(runtime) == ["True", "locked", "missing"]


def test_text_area_ctrl_enter_inside_form_stays_pending_until_submit(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

with st.form("editor"):
    value = st.text_area("Prompt", value="draft", key="prompt")
    submitted = st.form_submit_button("Save")

st.write(submitted)
st.write(value)
st.write(st.session_state.get("prompt", "missing"))
''',
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            app.set_focus(text_area)
            text_area.move_cursor((0, len(text_area.text)))

            await pilot.press("enter", "n", "e", "w", "ctrl+enter")
            await pilot.pause()

            assert "prompt" not in runtime.session_state
            assert rendered_texts(runtime) == ["False", "draft\nnew", "missing"]

            await pilot.press("tab", "enter")
            await pilot.pause()

            assert runtime.session_state["prompt"] == "draft\nnew"
            assert rendered_texts(runtime) == [
                "True",
                "draft\nnew",
                "draft\nnew",
            ]

    asyncio.run(scenario())


def test_text_area_enter_adds_newline_and_ctrl_enter_commits(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

value = st.text_area("Prompt", value="first", key="prompt")
st.write(value)
''',
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            app.set_focus(text_area)
            text_area.move_cursor((0, len(text_area.text)))

            await pilot.press("enter", "s", "e", "c", "o", "n", "d")
            await pilot.pause()

            assert text_area.text == "first\nsecond"
            assert runtime.session_state["prompt"] == "first"

            await pilot.press("ctrl+enter")
            await pilot.pause()

            committed = app.query_one(StuiTextArea)
            assert runtime.session_state["prompt"] == "first\nsecond"
            assert committed.text == "first\nsecond"
            assert app.focused is committed

    asyncio.run(scenario())


def test_text_area_max_chars_applies_during_editing(tmp_path: Path) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

st.text_area("Prompt", key="prompt", max_chars=4)
''',
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test() as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            app.set_focus(text_area)

            await pilot.press("a", "b", "c", "d", "e", "λ")
            await pilot.pause()
            assert text_area.text == "abcd"

            await pilot.press("ctrl+enter")
            await pilot.pause()
            assert runtime.session_state["prompt"] == "abcd"

    asyncio.run(scenario())


def test_text_area_max_chars_normalizes_before_live_replace_truncation(
    tmp_path: Path,
) -> None:
    script = write_script(
        tmp_path,
        '''
import stui as st

st.text_area("Prompt", key="prompt", max_chars=4)
''',
    )

    async def scenario() -> None:
        app = StuiApp(Runtime(script))
        async with app.run_test(headless=True) as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            text_area.replace("A\x1bBλC", (0, 0), (0, 0))
            await pilot.pause()

            assert text_area.text == "A\\x1"

    asyncio.run(scenario())


def test_text_area_preserves_cursor_scroll_and_renders_narrow(tmp_path: Path) -> None:
    value = "\n".join(f"line {index} " + "x" * 30 for index in range(20))
    script = write_script(
        tmp_path,
        f'''
import stui as st

st.text_area(
    "A very long prompt label that must remain safe in a narrow terminal",
    value={value!r},
    key="prompt",
    height=7,
)
''',
    )

    async def scenario() -> None:
        runtime = Runtime(script)
        app = StuiApp(runtime)

        async with app.run_test(size=(32, 14)) as pilot:
            await pilot.pause()
            text_area = app.query_one(StuiTextArea)
            app.set_focus(text_area)
            text_area.move_cursor((12, 5))
            text_area.scroll_to(y=10, animate=False, force=True, immediate=True)
            await pilot.pause()
            scroll_y = text_area.scroll_offset.y

            await pilot.press("ctrl+enter")
            await pilot.pause()

            restored = app.query_one(StuiTextArea)
            assert restored.cursor_location == (12, 5)
            assert scroll_y > 0
            assert restored.scroll_offset.y > 0
            assert app.focused is restored
            assert restored.size.width <= 32

    asyncio.run(scenario())
