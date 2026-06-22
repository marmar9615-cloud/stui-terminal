# stui v1.2.0

`stui` v1.2.0 is a practical post-v1 improvement release for
`stui-terminal`, the PyPI package that provides the `stui` import package and
the `stui` CLI.

This release keeps the package/import/CLI contract intact:

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

`stui` remains Streamlit-inspired, not official Streamlit, not affiliated with
Streamlit, and not a Streamlit compatibility layer. It still does not add a
browser, local server, websocket runtime, port-forwarding flow, Streamlit
runtime dependency, `textual-slider`, pandas, or heavy plotting dependency.

## What Changed

v1.2.0 focuses on validation, terminal polish, and data-display usefulness:

- Added `stui check APP.py` for non-interactive app validation.
- Added `stui check APP.py --json` for CI-friendly validation output.
- Added a repeatable custom external project validator at
  `scripts/verify_custom_project.sh`.
- Graduated `st.columns(count)` to the stable v1 API as a simple count-only
  terminal grouping primitive.
- Added `max_rows` and `max_cols` to `st.table` and `st.dataframe`.
- Improved chart empty states and list-of-dicts support for `st.line_chart`.

## CLI Validation

`stui check` runs an app through the `stui` runtime without launching the full
interactive Textual UI:

```bash
stui check app.py
stui check app.py --json
```

It exits with:

- `0` when the script renders successfully.
- `1` when the script runs but renders an internal app error.
- `2` when the script path is invalid.

The JSON output includes a schema version, resolved script path, status,
exit code, rendered element summary, and error details when validation fails.

## Data And Layout Improvements

`st.table` and `st.dataframe` now accept:

```python
st.table(data, max_rows=10, max_cols=6)
st.dataframe(data, max_rows=10, max_cols=6)
```

When data is truncated, the terminal output includes visible row/column markers
instead of silently hiding data.

`st.columns(count)` is now stable for the existing count-only behavior. It
preserves render order, supports nested content, and stacks vertically in narrow
terminals. More advanced column ratios, gutters, tabs, sidebars, and full layout
systems remain deferred.

## Chart Hardening

The chart APIs remain experimental, but v1.2.0 makes them less surprising:

- Unsupported or all-invalid chart data now renders `No chart data`.
- Non-finite values are ignored instead of producing misleading bars or lines.
- `st.line_chart` can infer numeric series from simple lists of dictionaries.
- Invalid chart sizes render readable API errors instead of raw type errors.
- Chart `width` and `height` values must be positive integers when provided.

## API Stability

Stable in v1.2.0:

- v1.0 stable core APIs.
- v1.1 graduated APIs: `st.json`, `st.progress`, `st.table`,
  `st.dataframe`, `st.metric`, `st.number_input`, `st.selectbox`, `st.radio`,
  `st.form`, `st.form_submit_button`, `st.container`, `st.expander`,
  `st.rerun`, and `st.stop`.
- `st.columns(count)`.

Still experimental:

- `st.bar_chart`
- `st.line_chart`
- `st.status`
- `st.spinner`
- `st.help`

Deferred:

- `st.empty`
- `st.tabs`
- full layout system
- sidebar
- file uploads
- caching
- dataframe editing
- heavier charting
- browser/server runtime

## Upgrade Notes

No public API was removed or renamed. Existing v1.1.0 scripts should continue
to work. The main behavior changes are additive: `stui check`, table/dataframe
limits, clearer chart empty states, and stable `st.columns(count)`.

## Verification Summary

The release must pass the standard v1 release gates before publication:

- editable install with dev dependencies
- Ruff
- `python3.11 -m pytest`
- build and Twine check
- `stui --version`
- `python -m stui --version`
- `./scripts/check.sh`
- `scripts/verify_custom_project.sh`
- exhaustive CLI command checks from the repository checkout
- clean wheel install in a temporary virtual environment
- fresh PyPI install after publish
- GitHub CI on `main` and `v1.2.0`
- GitHub Actions Trusted Publishing to PyPI
