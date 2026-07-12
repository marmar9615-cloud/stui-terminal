# stui v2.3.0

`stui` v2.3.0 is the interactive-workspaces-and-deep-diagnostics release. It
keeps the v2 stable contract compatible while making terminal apps easier to
organize, inspect, and use with local paths and data.

`stui` is Streamlit-inspired, not official Streamlit, not affiliated with
Streamlit, and not a Streamlit compatibility layer. It remains terminal-native:
no browser, server, websocket, port, or Streamlit runtime dependency.

## Install

```bash
python -m pip install --upgrade stui-terminal==2.3.0
stui demo workspace
```

The distribution remains `stui-terminal`, the import remains `stui`, and the
CLI remains `stui`.

## Interactive Workspaces

`st.tabs` is a post-v2 experimental workspace primitive:

```python
overview, data = st.tabs(["Overview", "Data"], key="workspace")

with overview:
    st.metric("Runs", 12)

with data:
    selected = st.data_table(rows, selection_mode="single", key="rows")
```

Every tab block executes in normal top-to-bottom script order. Only the active
pane's elements are mounted, visible, and focusable. Active state persists in
the normal widget pipeline; callbacks run after state update, forms defer the
change until submit, and nested tabs are supported. Left/Right and mouse clicks
switch tabs. The safe command palette exposes only visible tab groups.

## Local Paths

`st.path_input` is a post-v2 experimental text-first local path control. It
returns a normalized absolute string, resolves relative values from `root` or
the app directory, expands `~`, and never expands environment variables. It can
validate file/directory kind, existence, readability, and suffixes without
opening or parsing the target.

`root` is not a security sandbox. The `browse` flag reserves the experimental
call shape, but v2.3 does not ship a directory-tree overlay.

## Selectable Data

`st.data_table` is post-v2 experimental. It supports the documented static
table shapes without pandas and can return a selected source-row index for
`selection_mode="single"`. Display limits never renumber source rows. Arrow
keys move, Enter/Space selects, and mouse selection works where supported.
Editing, sorting, filtering, pagination, multiple selection, and row-object
returns remain out of scope. Populated non-selectable tables remain focusable
for keyboard scrolling without writing selection state.

## Diagnostics And Commands

```bash
stui inspect app.py
stui inspect app.py --json
stui inspect app.py --strict --repeat 3
```

The versioned `stui.inspect.v1` report includes package versions, normalized
paths, run timings, element/widget/key counts, nesting, local module/watch-file
counts, and aggregate cache counts. It never includes session values, cache
arguments/results, environment values, file contents, or arbitrary object
representations. App stdout/stderr is discarded during inspection so JSON stays
valid and non-sensitive.

Ctrl+P opens a fixed command palette with rerun, quit, theme toggle, app-scoped
cache clearing, focus-next, count-only diagnostics, help, and visible tab
switching. Tabs inside inactive panes or collapsed groups are omitted. There is
no shell execution, Python evaluation, custom command registration, or network
behavior.

## Stable API Graduations

The following APIs graduate to stable in v2.3.0:

- `st.cache_data`
- `st.cache_resource`
- `st.text_area`
- `st.toggle`

`st.multiselect`, `st.toast`, `st.status`, `st.spinner`, and `st.help` remain
experimental. New `st.tabs`, `st.path_input`, and `st.data_table` also begin as
post-v2 experimental APIs.

## Installed-User Flow

New offline bundled demos and a workspace starter are available without a repo
checkout:

```bash
stui demo list
stui demo workspace
stui demo tabs
stui demo data_explorer
stui demo diagnostics
stui init app.py --template workspace
stui check app.py --strict --repeat 2
stui inspect app.py --json
stui run app.py
```

The README and PyPI page use four real Textual captures from that workspace
demo, covering selectable data, narrow rendering, local path input, and the
fixed command palette. Reproduction details live in `docs/visual-proof.md`.

## Upgrade Notes

No stable API is removed or renamed. Apps using the v2.2 stable surface require
no migration. Experimental `st.multiselect` now rejects duplicate options with
a readable error; use unique options so selection identity remains clear.

## Verification

The release is published only after Ruff, the complete Python 3.11 test suite,
build, Twine, package-content audit, repo hygiene, exhaustive CLI/TUI checks,
clean wheel installation, custom multi-file project validation, security/static
review, macOS/Windows installed-wheel jobs, main/tag CI, Trusted Publishing,
public PyPI metadata, and a fresh exact-version install all pass.

## Deliberate Limits

- No path-tree overlay or sandbox claim.
- No table editing, sorting, filtering, pagination, or pandas dependency.
- No arbitrary command palette extension or shell execution.
- No sidebar, placeholder mutation, browser renderer, local server, websocket,
  port-forwarding workflow, file upload, or heavy plotting dependency.
