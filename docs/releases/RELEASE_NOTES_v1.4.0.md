# stui v1.4.0

`stui` v1.4.0 is a focused chart-contract and terminal-compatibility release.
It keeps the v1 package/import/CLI contract intact while making compact
terminal charts stable enough for real local dashboards and making terminal
compatibility reports easier to collect.

Install:

```bash
python -m pip install stui-terminal==1.4.0
```

Import and run:

```python
import stui as st
```

```bash
stui run app.py
```

## Highlights

- `st.bar_chart` and `st.line_chart` are now v1-stable compact terminal
  summaries.
- Charts now support simple tuple-pair inputs such as
  `[("baseline", -3), ("candidate", 7)]`.
- Charts now support common dict-of-columns data, including numeric
  `value`, `score`, `count`, `total`, or `y` columns for bar charts and
  numeric series columns for line charts.
- `stui doctor --compat` prints a concise terminal compatibility report for
  bug reports.
- `stui doctor --json` now includes `schema_version` and a structured
  compatibility object.

## Stable API Change

The following APIs graduate from post-v1 experimental to v1-stable in this
release:

- `st.bar_chart(data, *, width=None, height=None)`
- `st.line_chart(data, *, width=None, height=None)`

They are stable as compact terminal summaries, not plotting-library
replacements. They intentionally do not promise browser-style interactivity,
plotly/matplotlib parity, editable data, or heavy dataframe integration.

## Chart Data Shapes

`st.bar_chart` supports:

- numeric scalars
- lists or tuples of numbers
- dictionaries of numbers
- simple `(label, value)` pairs
- simple lists of dictionaries
- dict-of-column shapes with a numeric `value`, `score`, `count`, `total`, or
  `y` column

`st.line_chart` supports:

- numeric scalars
- lists or tuples of numbers
- dictionaries of numeric series
- simple `(label, value)` pairs
- simple lists of dictionaries
- dict-of-column shapes with numeric series

Non-finite values are ignored. Unsupported or all-invalid data renders
`No chart data`.

## Terminal Compatibility

`stui doctor --compat` is the preferred concise compatibility report for
terminal issues:

```bash
stui doctor --compat
stui doctor --json
```

The JSON output includes a compatibility profile, minimum recommended terminal
size, TTY status, and notes that are easier to compare across local terminals,
SSH sessions, containers, and editor terminals.

## Still Experimental

The remaining post-v1 experimental top-level APIs are:

- `st.status`
- `st.spinner`
- `st.help`

## Still Deferred

These features remain intentionally deferred:

- `st.empty`
- `st.tabs`
- full layout system
- sidebar
- file upload
- caching decorators
- dataframe editing
- heavier charting
- browser/server/websocket runtime

## Upgrade Notes

No public APIs were removed or renamed. Existing v1.3.0 apps should continue to
run. Users who were already using `st.bar_chart` or `st.line_chart` should see
the same broad behavior with additional accepted input shapes.

## Verification

This release is intended to be published only after the full release gates pass:
local lint/tests/build/Twine, package contents audit, repo hygiene audit,
exhaustive CLI checks, clean wheel install, custom external project validation,
GitHub CI, PyPI publish, GitHub Release creation, and fresh PyPI install.
