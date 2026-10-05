from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, InvalidOperation

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Input, Select, Static

from .._terminal_text import visible_terminal_text
from ..elements import DataTableElement
from .data_table import StuiDataTable


def _sort_value(value: str) -> tuple[int, Decimal | str]:
    """Sort finite numeric display values numerically, then casefolded text."""
    try:
        number = Decimal(value)
    except InvalidOperation:
        pass
    else:
        if number.is_finite():
            return (0, number)
    return (1, value.casefold())


class ExplorerSearch(Input):
    def replace(self, text: str, start: int, end: int) -> None:
        super().replace(visible_terminal_text(text), start, end)


class ExplorerTable(StuiDataTable):
    BINDINGS = [Binding("f4", "explore", "Explore table", show=False)]


class DataExplorerScreen(ModalScreen[int | None]):
    """Browse one rendered table snapshot without executing the app script."""

    DEFAULT_CSS = """
    DataExplorerScreen {
        background: #101014;
        padding: 0 1;
    }
    DataExplorerScreen #explorer-title {
        height: 2;
        padding: 0 1;
        background: #202033;
        color: #8ab4ff;
        text-style: bold;
    }
    DataExplorerScreen #explorer-search {
        margin: 0;
    }
    DataExplorerScreen #explorer-toolbar {
        height: 3;
    }
    DataExplorerScreen #explorer-sort {
        width: 1fr;
    }
    DataExplorerScreen #explorer-reverse {
        min-width: 10;
        width: 10;
        margin: 0 0 0 1;
    }
    DataExplorerScreen #explorer-summary {
        height: auto;
        max-height: 3;
        color: #a2a4b3;
    }
    DataExplorerScreen #explorer-content {
        height: 1fr;
    }
    DataExplorerScreen #explorer-grid {
        width: 2fr;
        height: 1fr;
        min-height: 3;
    }
    DataExplorerScreen #explorer-detail-panel {
        width: 1fr;
        height: 1fr;
        min-height: 3;
        border-left: solid #8ab4ff;
        padding: 0 1;
    }
    DataExplorerScreen.narrow #explorer-content {
        layout: vertical;
    }
    DataExplorerScreen.narrow #explorer-grid {
        width: 100%;
    }
    DataExplorerScreen.narrow #explorer-detail-panel {
        width: 100%;
        border-left: none;
        border-top: solid #8ab4ff;
    }
    .stui-high-contrast DataExplorerScreen #explorer-title {
        background: #000000;
        color: #ffff00;
    }
    .stui-high-contrast DataExplorerScreen #explorer-summary {
        color: #ffffff;
    }
    """
    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("ctrl+f", "search", "Search"),
        Binding("f6", "sort_next", "Sort column"),
        Binding("f7", "reverse", "Reverse"),
        Binding("f8", "reset", "Reset", show=False),
    ]

    def __init__(
        self, element: DataTableElement, *, cursor_row: int = 0
    ) -> None:
        super().__init__()
        # Only the normalized, display-limited data enters the explorer.
        self.element = element
        self._rows = dict(zip(element.source_row_indices, element.rows))
        self._search_rows = {
            index: tuple(visible_terminal_text(cell).casefold() for cell in row)
            for index, row in self._rows.items()
        }
        self._sort_column = -1
        self._reverse = False
        self._cursor_row = cursor_row

    def compose(self) -> ComposeResult:
        yield Static("DATA EXPLORER", id="explorer-title")
        search = ExplorerSearch(
            placeholder="Search all displayed columns...",
            id="explorer-search",
        )
        search.styles.margin = 0
        yield search
        with Horizontal(id="explorer-toolbar"):
            yield Select(
                [("Source order", -1)]
                + [
                    (Text(visible_terminal_text(header)), index)
                    for index, header in enumerate(self.element.headers)
                ],
                value=-1,
                allow_blank=False,
                id="explorer-sort",
                tooltip="Sort column. F6 cycles columns; F8 restores source order.",
            )
            reverse = Button("Ascending", id="explorer-reverse", disabled=True)
            reverse.styles.margin = (0, 0, 0, 1)
            yield reverse
        yield Static(id="explorer-summary")
        with Horizontal(id="explorer-content"):
            table = ExplorerTable(
                replace(self.element, selection_mode="single", height=None),
                cursor_row=self._cursor_row,
                id="explorer-grid",
            )
            table.styles.height = "1fr"
            table.styles.width = "2fr"
            yield table
            with VerticalScroll(id="explorer-detail-panel"):
                yield Static(id="explorer-details")
        yield Footer()

    def on_mount(self) -> None:
        self._resize_layout()
        table = self.query_one("#explorer-grid", StuiDataTable)
        table.focus()
        self._refresh_summary()
        self._show_details()

    def on_resize(self) -> None:
        self._resize_layout()

    def _resize_layout(self) -> None:
        self.set_class(self.size.width < 72, "narrow")
        for table in self.query(StuiDataTable):
            table.styles.width = "100%" if self.size.width < 72 else "2fr"

    def action_close(self) -> None:
        self.dismiss(None)

    def action_search(self) -> None:
        self.query_one("#explorer-search", Input).focus()

    def action_sort_next(self) -> None:
        count = len(self.element.headers)
        self.query_one("#explorer-sort", Select).value = (
            (self._sort_column + 2) % (count + 1) - 1
        )

    def action_reverse(self) -> None:
        if self._sort_column >= 0:
            self._reverse = not self._reverse
            self._refresh_rows()

    def action_reset(self) -> None:
        self.query_one("#explorer-search", Input).value = ""
        self.query_one("#explorer-sort", Select).value = -1
        self._sort_column = -1
        self._reverse = False
        self._refresh_rows()

    @on(Input.Changed, "#explorer-search")
    def search_changed(self, event: Input.Changed) -> None:
        event.stop()
        self._refresh_rows()

    @on(Input.Submitted, "#explorer-search")
    def search_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.query_one("#explorer-grid", StuiDataTable).focus()

    @on(Select.Changed, "#explorer-sort")
    def sort_changed(self, event: Select.Changed) -> None:
        event.stop()
        if isinstance(event.value, int):
            self._sort_column = event.value
            self._reverse = False
            self._refresh_rows()

    @on(Button.Pressed, "#explorer-reverse")
    def reverse_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.action_reverse()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        event.stop()
        if event.column_index == self._sort_column:
            self.action_reverse()
        else:
            self.query_one("#explorer-sort", Select).value = event.column_index

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        event.stop()
        self._show_details()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        event.stop()
        table = self.query_one("#explorer-grid", StuiDataTable)
        source_index = table.source_index_for_row(event.cursor_row)
        if self.element.selection_mode == "single" and source_index is not None:
            self.dismiss(source_index)

    def on_stui_data_table_explore(self, event: StuiDataTable.Explore) -> None:
        # F4 inside the explorer must not open a second copy.
        event.stop()

    def _refresh_rows(self) -> None:
        table = self.query_one("#explorer-grid", StuiDataTable)
        previous = table.source_index_for_row(table.cursor_row)
        terms = self.query_one("#explorer-search", Input).value.casefold().split()
        indices = [
            index
            for index, cells in self._search_rows.items()
            if all(any(term in cell for cell in cells) for term in terms)
        ]
        if self._sort_column >= 0:
            indices.sort(
                key=lambda index: _sort_value(self._rows[index][self._sort_column]),
                reverse=self._reverse,
            )
        table.clear()
        table.stui_source_row_indices = tuple(indices)
        for index in indices:
            table.add_row(
                *(
                    Text(
                        visible_terminal_text(cell),
                        style="bold" if index == self.element.selected_index else "",
                        overflow="ellipsis",
                        no_wrap=True,
                    )
                    for cell in self._rows[index]
                ),
                key=f"source-{index}",
            )
        table.show_cursor = bool(indices)
        table.move_cursor(
            row=indices.index(previous) if previous in indices else 0,
            column=0,
        )
        self._refresh_summary()
        self._show_details()

    def _refresh_summary(self) -> None:
        table = self.query_one("#explorer-grid", StuiDataTable)
        count = len(table.stui_source_row_indices)
        summary = f"{count} / {len(self._rows)} rows"
        if self.element.hidden_rows:
            summary += f" · {self.element.hidden_rows} outside max_rows"
        summary += (
            " · Enter selects"
            if self.element.selection_mode == "single"
            else " · Read-only"
        )
        self.query_one("#explorer-summary", Static).update(Text(summary))
        reverse = self.query_one("#explorer-reverse", Button)
        reverse.disabled = self._sort_column < 0
        reverse.label = "Descending" if self._reverse else "Ascending"

    def _show_details(self) -> None:
        table = self.query_one("#explorer-grid", StuiDataTable)
        index = table.source_index_for_row(table.cursor_row)
        detail = Text()
        if index is None:
            detail.append("No matching rows\n", style="bold")
            detail.append("Change the search or press F8 to reset.")
        else:
            detail.append(f"SOURCE ROW {index}\n", style="bold")
            for header, cell in zip(self.element.headers, self._rows[index]):
                detail.append(f"\n{visible_terminal_text(header)}\n", style="bold")
                detail.append(f"{visible_terminal_text(cell)}\n")
        self.query_one("#explorer-details", Static).update(detail)
        self.query_one("#explorer-detail-panel", VerticalScroll).scroll_home(
            animate=False
        )
