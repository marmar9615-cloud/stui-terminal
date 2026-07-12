# Interactive Data

`st.data_table` is a post-v2 experimental, terminal-native table with optional
single-row selection. It is separate from the stable, static `st.table` and
`st.dataframe` APIs. It does not change their behavior.

```python
selected_index = st.data_table(
    data,
    selection_mode="single",
    key="runs",
    disabled=False,
    on_select=record_selection,
    args=(),
    kwargs={},
    max_rows=20,
    max_cols=8,
    height=10,
    show_index=True,
)
```

The full signature is:

```text
st.data_table(data, *, selection_mode=None, key=None, disabled=False,
              on_select=None, args=None, kwargs=None, max_rows=None,
              max_cols=None, height=None, show_index=False) -> int | None
```

## Selection Contract

`selection_mode` accepts only:

- `None`: render a non-selectable table and return `None`.
- `"single"`: return one zero-based source row index or `None`.

The return value is always a positional source index, never a row object or a
dataframe index label. `show_index=True` displays those same source positions
in a leading `#` column.

Selection is stored in `st.session_state` under the explicit `key`, or under a
deterministic generated key when `key` is omitted. A selected index persists
while that position still exists in the normalized source data. If the source
shrinks past it, selection resets to `None`. Replacing or reordering rows while
keeping the same length preserves the numeric position, so use a stable widget
key and clear its state when position-based carryover is not appropriate.

`max_rows` and `max_cols` are display limits only. They do not change source
row numbering or invalidate a still-valid selection. Only mounted visible rows
can receive cursor or selection events. A selection hidden by a smaller
`max_rows` therefore remains the return value until the source index itself is
invalid or the app clears it.

Invalid queued values, including booleans, negative indexes, strings, floats,
and out-of-range indexes, are ignored. They do not replace a valid selection
or invoke `on_select`.

## Interaction

Up and Down move the row cursor. Enter or Space selects the highlighted row and
reruns the script through the normal widget path. The cursor survives rerenders
by widget key and clamps to the last visible row when displayed data shrinks.
An empty table has no cursor and is skipped by focus traversal.

Mouse selection uses Textual's row behavior: the first click highlights a row,
and clicking the highlighted row selects it. This path is covered by the
Textual Pilot harness. Keyboard interaction remains the baseline.

When `disabled=True`, pending interaction is ignored, the table is skipped by
focus traversal, and any still-valid stored selection remains unchanged.

`on_select` accepts `args` and `kwargs`. Outside a form, state is updated before
the callback runs. Inside `st.form`, the selected value is pending until the
form submit button commits it; `session_state` and `on_select` update together
on submit.

## Data And Display

`st.data_table` reuses the stable table normalization rules. Supported inputs
include:

- lists or tuples of dictionaries, dataclasses, named tuples, or public
  attribute objects;
- lists or tuples of row sequences;
- dictionaries of column sequences and ordinary key/value dictionaries;
- scalar and one-dimensional sequence values;
- dataframe-like objects exposing `columns` and `to_dict(orient="records")`.

No dataframe package is required at runtime.

`max_rows`, `max_cols`, and `height` must be positive integers or `None`.
`show_index` must be a boolean. When `height` is omitted, the widget fits its
header and visible rows up to a 10-row terminal height; larger tables scroll.
An explicit height fixes that terminal height.

Multiline cells use the existing single-row normalization, tabs become spaces,
and Unicode text is preserved. Cell widths are bounded, long values use
ellipsis rendering, and the Textual table scrolls within narrow terminals
instead of widening the containing layout.

## Layout Compatibility

Interactive tables mount recursively inside `st.container`, `st.columns`,
expanders, status blocks, spinners, and forms. Wide columns render side by side;
the existing columns renderer stacks them when the available width is too
narrow.

The v2.2 baseline used for this isolated implementation does not expose
`st.tabs`, so table-in-tab behavior is not claimed by this proof. The accepted
v2.3 architecture requires only the active tab block to mount. Integration
must verify keyboard focus, cursor restoration, and hidden-tab event isolation
after the tabs workstream is merged.

## Non-Goals

The initial contract does not include cell editing, sorting, filtering,
multiple selection, dataframe row labels, or returning mutable row data.
`st.table` and `st.dataframe` remain the stable static-display choices.

## Proof

```bash
python3.11 -m pytest tests/test_data_table.py
python3.11 -m pytest
```

The focused suite covers normalization, defensive state, data changes,
callbacks, forms, keyboard and mouse selection, cursor persistence, disabled
and empty states, explicit height, Unicode and long cells, narrow terminals,
and columns.
