# stui v1.1.0

`stui` v1.1.0 is the first post-v1 improvement release for
`stui-terminal`, the PyPI package that provides the `stui` import package and
the `stui` CLI.

This release keeps the v1.0.0 package/import/CLI contract intact:

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
runtime dependency, `textual-slider`, or heavy dataframe/charting dependency.

## What Changed

v1.1.0 graduates the safest experimental APIs into the stable v1 contract:

- `st.json`
- `st.progress`
- `st.table`
- `st.dataframe`
- `st.metric`
- `st.number_input`
- `st.selectbox`
- `st.radio`
- `st.form`
- `st.form_submit_button`
- `st.container`
- `st.expander`
- `st.rerun`
- `st.stop`

These APIs now sit alongside the v1.0 stable core. Their public names, call
shapes, return values, and basic behavior should remain compatible through the
v1 series unless a correctness, terminal, or security issue forces a documented
change.

## Still Experimental

These APIs remain public but post-v1 experimental:

- `st.columns`
- `st.bar_chart`
- `st.line_chart`
- `st.status`
- `st.spinner`
- `st.help`

They are useful enough to keep trying, but their layout, chart, grouping, and
formatting contracts still need more terminal evidence before they become
stable.

## Runtime And State Hardening

- Generated widget keys now conflict correctly with explicit user keys in the
  same run instead of silently creating duplicate widget identities.
- Form widget callbacks now run after every pending form value has committed to
  `st.session_state`, so callbacks can see the whole submitted form state.
- `st.stop()` and `st.rerun()` use internal control-flow exceptions that are not
  swallowed by broad user `except Exception` blocks.
- Session-state rollback after script exceptions now deep-copies ordinary
  mutable values where possible, reducing accidental leaks from in-place
  mutation.

## Display And Data Hardening

- `st.json` now handles mixed and non-string mapping keys by stringifying keys
  for display.
- `st.progress` rejects booleans and non-finite numeric values with readable API
  errors, while finite values continue to normalize and clamp to 0-100.
- `st.table` and `st.dataframe` now preserve list-of-dicts data with non-string
  keys.
- Static table/dataframe docs now spell out supported input shapes: scalars,
  lists/tuples of scalars, lists/tuples of dicts, lists/tuples of lists/tuples,
  dicts of scalar values, dicts of list/tuple columns, and pandas-like objects
  with `.columns` plus `.to_dict(orient="records")`.

## Installed-User CLI Polish

- `stui demo list` now reports demos that are actually available in bundled
  package resources.
- `stui doctor --json` now warns when the imported `stui` version and installed
  `stui-terminal` distribution metadata disagree.
- `stui example copy` has more coverage around directory destinations and
  no-overwrite behavior.
- `stui init` now reports a clearer error when the target path is a directory,
  even if it ends in `.py`.

## Upgrade Notes

No public API was removed or renamed. Existing v1.0.0 scripts should continue
to work. The main behavior tightening is stricter error reporting for duplicate
widget keys, invalid progress values, and invalid CLI destinations.

## Verification Summary

The release must pass the standard v1 release gates before publication:

- editable install with dev dependencies
- Ruff
- `python3.11 -m pytest`
- build and Twine check
- `stui --version`
- `python -m stui --version`
- `./scripts/check.sh`
- clean wheel install in a temporary virtual environment
- fresh PyPI install after publish
- GitHub CI on `main` and `v1.1.0`
- GitHub Actions Trusted Publishing to PyPI

