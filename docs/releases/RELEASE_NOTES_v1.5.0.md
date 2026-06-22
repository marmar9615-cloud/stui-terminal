# stui v1.5.0

`stui` v1.5.0 is a focused data-display and layout-refinement release for
`stui-terminal`. It keeps the public API stable while making common terminal
tables and nested layouts behave more predictably.

Install or upgrade:

```bash
python -m pip install --upgrade stui-terminal==1.5.0
```

Then import and run as usual:

```python
import stui as st
```

```bash
stui run app.py
```

## Highlights

- Improved `st.table` and `st.dataframe` static display for dataclasses,
  namedtuples, simple public objects, uneven rows, empty tables, and multiline or
  tabbed cell values.
- Preserved `max_cols` truncation markers like `+14 cols` when terminal-width
  trimming also applies.
- Rendered empty tables with a readable `No rows` marker instead of a blank body.
- Refined count-only `st.columns` so nested column groups stack based on their
  parent column width, not the full terminal width.
- Updated bundled `data_display` and `layouts` examples to show static data
  limits, object rows, grouped tables, explicit expander keys, and installed-user
  copy/run flows.

## Data Display

`st.table(data)` and `st.dataframe(data)` remain static terminal displays. They
do not require pandas and do not add editing, sorting, or selection. v1.5.0
extends and documents the supported display shapes:

- scalars;
- lists or tuples of scalars;
- lists or tuples of dicts;
- lists or tuples of lists/tuples;
- dicts of scalar values;
- dicts of lists/tuples;
- dataclass instances;
- namedtuple-like objects;
- simple objects with public attributes;
- pandas-like objects with `to_dict(orient="records")` and `columns`.

Use `max_rows` and `max_cols` to keep output compact. Hidden rows and columns are
shown with visible `+N rows` and `+N cols` markers.

## Layout

`st.columns(count)` remains stable and intentionally modest:

- integer `count` only;
- no ratios, custom gaps, sidebars, tabs, or browser-grid behavior;
- side-by-side rendering when the available width is large enough;
- vertical stacking in narrow terminals;
- nested columns stack according to parent width.

Tabs remain deferred. Use headings, containers, columns, and expanders for the v1
layout surface.

## Compatibility

No public APIs were removed, renamed, or intentionally broken. Existing v1.4.0
apps should continue to run. v1.5.0 is a refinement release, not a new feature
wave.

The package boundary remains:

- PyPI distribution: `stui-terminal`
- import package: `stui`
- CLI command: `stui`

## Verification

The release was prepared with the standard gates:

- local editable install
- Ruff
- pytest
- build
- Twine check
- package contents audit
- repo hygiene audit
- CLI command checks
- clean wheel install
- custom external project validation
- CI on GitHub
- Trusted Publishing to PyPI
- fresh exact PyPI install after publish
