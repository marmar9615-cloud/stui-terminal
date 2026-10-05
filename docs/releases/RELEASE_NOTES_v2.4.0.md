# stui v2.4.0

`stui` v2.4.0 adds a fullscreen explorer to existing `st.data_table` widgets.
The public signatures, stable API contract, and dependencies are unchanged.
`st.data_table` remains experimental.

`stui` is Streamlit-inspired, not official Streamlit, not affiliated with
Streamlit, and not a Streamlit compatibility layer. It remains terminal-native,
with no browser, server, websocket, or Streamlit runtime dependency.

## Install

```bash
python -m pip install --upgrade stui-terminal==2.4.0
python -m stui demo data_explorer
```

Focus the table and press F4, or choose its Explore table action from Ctrl+P.
The bundled Run lab demo contains 24 synthetic benchmarks.

## Fullscreen Data Explorer

- Live, case-insensitive search across displayed cells.
- Numeric-aware column sorting, stable ties, and original source order.
- Complete normalized row details in wide and narrow terminal layouts.
- Original source-row indexes preserved after sorting and filtering.
- Selection through the existing callback and pending-form pipeline.
- Escape cancels without changing selection; browsing does not rerun scripts.
- Watch-mode reloads wait until the explorer closes.

Search also matches the visible escapes used for terminal control characters.
Source distributions include the real SVG preview captures.

## Limits And Upgrade Notes

Existing `st.data_table` calls gain the explorer without code changes. It uses
a snapshot of normalized data within `max_rows` and `max_cols`; it does not
retrieve hidden rows or columns, expose original Python objects, or edit cells.
Search and sort reset each time it opens. Static `st.table` and `st.dataframe`
behavior is unchanged. No new public sorting or filtering API is introduced.

See [Interactive Data](https://github.com/marmar9615-cloud/stui-terminal/blob/v2.4.0/docs/interactive-data.md#fullscreen-explorer) for controls
and selection semantics. Captures at 120x36 and 38x22 cells are real Textual
renders, not a claim of compatibility with every terminal emulator.

## Verification

Release gates include the complete Python 3.11 suite, Ruff, version consistency,
build and Twine checks, package-content audit, strict repeated self-tests,
clean-wheel installation, external multi-file cache/watch validation, explorer
interaction at wide and narrow sizes, main/tag CI, and a fresh exact-version
install from PyPI after Trusted Publishing.
