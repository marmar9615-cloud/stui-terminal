from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text
from textual.binding import Binding
from textual.widgets import DataTable

from .._terminal_text import visible_terminal_text
from ..elements import DataTableElement

MIN_COLUMN_WIDTH = 4
MAX_COLUMN_WIDTH = 24


class StuiDataTable(DataTable):
    BINDINGS = [
        *DataTable.BINDINGS,
        Binding("space", "select_cursor", "Select", show=False),
    ]

    def __init__(
        self,
        element: DataTableElement,
        *,
        cursor_row: int | None = None,
        id: str | None = None,
    ) -> None:
        focusable = bool(element.source_row_indices) and not element.disabled
        selectable = (
            element.selection_mode == "single"
            and focusable
        )
        self.stui_key = element.key
        self.stui_selection_mode = element.selection_mode
        self.stui_source_row_indices = element.source_row_indices
        self.stui_selected_index = element.selected_index
        super().__init__(
            show_header=True,
            show_row_labels=False,
            zebra_stripes=True,
            show_cursor=selectable,
            cursor_type="row" if selectable else "none",
            id=id,
            classes="stui-data-table-widget",
            disabled=element.disabled,
        )
        self.can_focus = focusable

        for column_index, header in enumerate(element.headers):
            values = (row[column_index] for row in element.rows)
            width = min(
                MAX_COLUMN_WIDTH,
                max(
                    MIN_COLUMN_WIDTH,
                    cell_len(visible_terminal_text(header)),
                    *(cell_len(visible_terminal_text(value)) for value in values),
                ),
            )
            self.add_column(
                Text(
                    visible_terminal_text(header),
                    overflow="ellipsis",
                    no_wrap=True,
                ),
                width=width,
                key=f"column-{column_index}",
            )

        for source_index, row in zip(element.source_row_indices, element.rows):
            selected_style = (
                "bold #d7ffdf" if source_index == element.selected_index else ""
            )
            self.add_row(
                *(
                    Text(
                        visible_terminal_text(cell),
                        style=selected_style,
                        overflow="ellipsis",
                        no_wrap=True,
                    )
                    for cell in row
                ),
                key=f"source-{source_index}",
            )

        self.styles.height = element.height or min(
            10,
            max(2, len(element.source_row_indices) + 1),
        )

        if element.source_row_indices:
            if cursor_row is None:
                try:
                    cursor_row = element.source_row_indices.index(
                        element.selected_index
                    )
                except ValueError:
                    cursor_row = 0
            clamped_cursor = min(
                max(cursor_row, 0),
                len(element.source_row_indices) - 1,
            )
            self.move_cursor(row=clamped_cursor, column=0, scroll=False)

    def source_index_for_row(self, cursor_row: int) -> int | None:
        if 0 <= cursor_row < len(self.stui_source_row_indices):
            return self.stui_source_row_indices[cursor_row]
        return None
