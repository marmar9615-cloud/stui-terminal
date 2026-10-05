import asyncio
from pathlib import Path

import pytest
from textual.widgets import Input, Select, Static

from stui.app import StuiApp
from stui.runtime import Runtime
from stui.widgets.data_explorer import DataExplorerScreen, _sort_value
from stui.widgets.data_table import StuiDataTable


def make_app(tmp_path: Path, options: str = '', *, form: bool = False) -> StuiApp:
    script = tmp_path / "app.py"
    table = f'''selected = st.data_table(
    [
        {{"name": "Alpha", "score": 100, "note": "ready 東京"}},
        {{"name": "Beta", "score": 9, "note": "needs review"}},
        {{"name": "Straße", "score": -2, "note": "ready 東京"}},
    ],
    key="rows", on_select=record, {options}
)
'''
    if form:
        table = (
            'with st.form("review"):\n'
            + "\n".join(f"    {line}" for line in table.splitlines())
            + '\n    st.form_submit_button("Save")\n'
        )
    script.write_text(
        '''import stui as st
st.session_state.runs = st.session_state.get("runs", 0) + 1
if "events" not in st.session_state:
    st.session_state.events = []
def record():
    st.session_state.events.append(st.session_state.rows)
'''
        + table,
        encoding="utf-8",
    )
    return StuiApp(Runtime(script))


async def open_explorer(app, pilot):
    app.query_one(StuiDataTable).focus()
    await pilot.press("f4")
    await pilot.pause()
    assert isinstance(app.screen, DataExplorerScreen)
    return app.screen


def test_search_sort_and_select_preserve_source_identity(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, 'selection_mode="single"')
        async with app.run_test(size=(100, 32)) as pilot:
            screen = await open_explorer(app, pilot)
            screen.query_one(Select).value = 1
            await pilot.pause()
            table = screen.query_one(StuiDataTable)
            assert table.stui_source_row_indices == (2, 1, 0)

            await pilot.press("ctrl+f")
            await pilot.press(*"ready 東京")
            await pilot.pause()
            assert table.stui_source_row_indices == (2, 0)
            assert app.runtime.session_state.runs == 1
            assert app.runtime.session_state.events == []
            assert app.runtime.session_state.rows is None

            await pilot.press("enter", "up", "enter")
            await pilot.pause()
            assert not isinstance(app.screen, DataExplorerScreen)
            assert app.runtime.session_state.rows == 2
            assert app.runtime.session_state.events == [2]
            assert app.runtime.session_state.runs == 2
            assert app.query_one(StuiDataTable).cursor_row == 2
            assert app.focused is app.query_one(StuiDataTable)

    asyncio.run(scenario())


def test_cancel_empty_search_and_reset_do_not_rerun(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, 'selection_mode="single"')
        async with app.run_test(size=(38, 22)) as pilot:
            original = app.query_one(StuiDataTable)
            screen = await open_explorer(app, pilot)
            assert screen.has_class("narrow")
            search = screen.query_one(Input)
            search.value = "STRASSE"
            await pilot.pause()
            assert screen.query_one(StuiDataTable).stui_source_row_indices == (2,)
            search.value = "missing"
            await pilot.pause()
            assert screen.query_one(StuiDataTable).row_count == 0
            assert "No matching rows" in str(
                screen.query_one("#explorer-details", Static).render()
            )
            await pilot.press("enter")
            assert isinstance(app.screen, DataExplorerScreen)
            await pilot.press("f8")
            await pilot.pause()
            assert screen.query_one(StuiDataTable).row_count == 3
            await pilot.press("escape")
            await pilot.pause()
            assert app.focused is original
            assert app.runtime.session_state.runs == 1
            assert app.runtime.session_state.rows is None

    asyncio.run(scenario())


def test_sort_shortcuts_header_clicks_and_cursor_follow_source(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, 'selection_mode="single"')
        async with app.run_test(size=(100, 30)) as pilot:
            screen = await open_explorer(app, pilot)
            table = screen.query_one(StuiDataTable)
            await pilot.press("f6", "f6")
            await pilot.pause()
            assert table.stui_source_row_indices == (2, 1, 0)
            assert table.source_index_for_row(table.cursor_row) == 0
            await pilot.press("f7")
            await pilot.pause()
            assert table.stui_source_row_indices == (0, 1, 2)
            # The second column is score, not a sorted view's source position.
            await pilot.click(table, offset=(12, 0))
            await pilot.pause()
            assert table.stui_source_row_indices == (2, 1, 0)
            await pilot.press("f8")
            await pilot.pause()
            assert table.stui_source_row_indices == (0, 1, 2)

    asyncio.run(scenario())


def test_explorer_selection_inside_form_stays_pending(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, 'selection_mode="single"', form=True)
        async with app.run_test() as pilot:
            await open_explorer(app, pilot)
            await pilot.press("down", "enter")
            await pilot.pause()
            assert "rows" not in app.runtime.session_state
            assert app.runtime.form_pending_values["review"]["rows"] == 1
            assert app.runtime.session_state.events == []
            await pilot.press("tab", "enter")
            await pilot.pause()
            assert app.runtime.session_state.rows == 1
            assert app.runtime.session_state.events == [1]

    asyncio.run(scenario())


def test_readonly_explorer_and_limits(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, "max_rows=2, max_cols=1")
        async with app.run_test() as pilot:
            screen = await open_explorer(app, pilot)
            assert screen.query_one(StuiDataTable).row_count == 2
            details = str(screen.query_one("#explorer-details", Static).render())
            assert "Alpha" in details
            assert "ready" not in details
            summary = str(screen.query_one("#explorer-summary", Static).render())
            assert "1 outside max_rows" in summary
            assert "Read-only" in summary
            await pilot.press("down", "enter", "space", "f4", "r", "q")
            await pilot.pause()
            assert app.screen is screen
            assert app.runtime.session_state.runs == 1
            assert app.runtime.session_state.rows is None

    asyncio.run(scenario())


def test_palette_explores_only_enabled_tables_and_limits_modal_commands(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app.run_test() as pilot:
            commands = {c.title: c for c in app.get_system_commands(app.screen)}
            commands["Explore table: rows"].callback()
            await pilot.pause()
            assert isinstance(app.screen, DataExplorerScreen)
            assert [c.title for c in app.get_system_commands(app.screen)] == [
                "Close data explorer"
            ]

        app = make_app(tmp_path, "disabled=True")
        async with app.run_test() as pilot:
            table = app.query_one(StuiDataTable)
            table.action_explore()
            await pilot.pause()
            assert not isinstance(app.screen, DataExplorerScreen)
            assert not any(
                c.title.startswith("Explore table:")
                for c in app.get_system_commands(app.screen)
            )

    asyncio.run(scenario())


def test_watch_reload_waits_until_explorer_closes(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, 'selection_mode="single"')
        async with app.run_test() as pilot:
            await open_explorer(app, pilot)
            script = app.runtime.script_path
            script.write_text('import stui as st\nst.write("Reloaded")\n')
            await app._poll_script_change()
            assert isinstance(app.screen, DataExplorerScreen)
            assert app.runtime.session_state.runs == 1
            await pilot.press("escape")
            await pilot.pause()
            await app._poll_script_change()
            assert not list(app.query(StuiDataTable))
            assert app.runtime.elements[0].text == "Reloaded"

    asyncio.run(scenario())


@pytest.mark.parametrize("size", [(120, 36), (38, 22)])
def test_details_are_untruncated_literal_and_responsive(
    tmp_path: Path, size: tuple[int, int]
) -> None:
    async def scenario() -> None:
        script = tmp_path / "app.py"
        long_value = "[bold]東京[/bold] " + "long value " * 30 + "\x1b[31m"
        script.write_text(f"import stui as st\nst.data_table([{long_value!r}])\n")
        app = StuiApp(Runtime(script))
        async with app.run_test(size=size) as pilot:
            screen = await open_explorer(app, pilot)
            detail = screen.query_one("#explorer-details", Static)
            rendered = str(detail.render())
            assert "[bold]東京[/bold]" in rendered
            assert "long value " * 30 in rendered
            assert "\\x1b[31m" in rendered
            assert "\x1b" not in app.export_screenshot()
            table = screen.query_one(StuiDataTable)
            panel = screen.query_one("#explorer-detail-panel")
            assert table.size.width <= size[0]
            assert panel.region.right <= size[0]
            assert panel.region.bottom <= size[1]
            if size[0] < 72:
                assert panel.region.y >= table.region.bottom
            else:
                assert panel.region.x >= table.region.right

    asyncio.run(scenario())


def test_sort_display_values_keeps_precision_and_handles_mixed_types() -> None:
    values = ["100", "9", "-2", "1.5", "1e3", "NaN", "apple", "9007199254740993",
              "9007199254740992", "Infinity"]
    assert sorted(values, key=_sort_value) == [
        "-2", "1.5", "9", "100", "1e3", "9007199254740992",
        "9007199254740993", "apple", "Infinity", "NaN",
    ]


def test_empty_table_opens_from_palette_and_resizes(tmp_path: Path) -> None:
    async def scenario() -> None:
        script = tmp_path / "empty.py"
        script.write_text('import stui as st\nst.data_table([], key="empty")\n')
        app = StuiApp(Runtime(script))
        async with app.run_test(size=(100, 30)) as pilot:
            app.action_toggle_theme()
            commands = {c.title: c for c in app.get_system_commands(app.screen)}
            commands["Explore table: empty"].callback()
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, DataExplorerScreen)
            assert screen.query_one(StuiDataTable).row_count == 0
            await pilot.resize_terminal(38, 22)
            await pilot.pause()
            assert screen.has_class("narrow")
            await pilot.resize_terminal(100, 30)
            await pilot.pause()
            assert not screen.has_class("narrow")
            panel = screen.query_one("#explorer-detail-panel")
            assert panel.region.right <= 100
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, DataExplorerScreen)

    asyncio.run(scenario())


def test_search_matches_visible_control_character_escapes(tmp_path: Path) -> None:
    async def scenario() -> None:
        script = tmp_path / "controls.py"
        script.write_text(
            "import stui as st\nst.data_table(['red\\x1b[31m', 'plain'])\n",
            encoding="utf-8",
        )
        app = StuiApp(Runtime(script))
        async with app.run_test() as pilot:
            screen = await open_explorer(app, pilot)
            await pilot.press("ctrl+f")
            await pilot.press(*r"\x1b")
            await pilot.pause()
            assert screen.query_one(StuiDataTable).stui_source_row_indices == (0,)

    asyncio.run(scenario())
