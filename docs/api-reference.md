# Public API Reference

`stui` is a small Streamlit-inspired terminal UI library. It is not official
Streamlit, is not affiliated with Streamlit, and is not a Streamlit
compatibility layer.

This page documents the supported public surface exposed by:

```python
import stui as st
```

Names not listed here should be treated as private implementation details,
including runtime classes, Textual widgets, and element dataclasses under
`stui.runtime`, `stui.app`, `stui.widgets`, and `stui.elements`.

## Public Imports

These names are intentionally exported from `stui.__all__`. Stability labels are
defined in [API Stability](api-stability.md).

<!-- API_CLASSIFICATION_START -->
| API | Classification | Notes |
| --- | --- | --- |
| `__version__` | v1-stable | Package version string. |
| `bar_chart` | v1-stable | Compact terminal bar summary, not plotting-library parity. |
| `button` | v1-stable | Core input widget. |
| `caption` | v1-stable | Core text output. |
| `checkbox` | v1-stable | Core input widget. |
| `code` | v1-stable | Core text output. |
| `columns` | v1-stable | Count-only responsive terminal columns that stack on narrow terminals. |
| `container` | v1-stable | Terminal grouping primitive, not a full layout engine. |
| `dataframe` | v1-stable | Static terminal display; editing and sorting are out of scope. |
| `divider` | v1-stable | Core visual separator. |
| `error` | v1-stable | Core status output. |
| `exception` | v1-stable | Core status output for exceptions. |
| `expander` | v1-stable | Keyboard-toggleable terminal grouping primitive. |
| `form` | v1-stable | Deferred submit behavior is part of the v1 contract. |
| `form_submit_button` | v1-stable | One-shot form submit button. |
| `header` | v1-stable | Core text output. |
| `help` | post-v1 experimental | Help formatting and the public name need more feedback. |
| `info` | v1-stable | Core status output. |
| `json` | v1-stable | Static terminal JSON display with string fallback. |
| `line_chart` | v1-stable | Compact terminal sparkline summary, not plotting-library parity. |
| `markdown` | v1-stable | Core text output. |
| `metric` | v1-stable | Compact terminal summary display. |
| `multiselect` | post-v2 experimental | Checkbox-style multi-option selection, new in v2.1.0. |
| `number_input` | v1-stable | Numeric input widget. |
| `progress` | v1-stable | Clamped terminal progress display. |
| `radio` | v1-stable | Selection input widget. |
| `rerun` | v1-stable | Flow-control helper for explicit reruns. |
| `selectbox` | v1-stable | Selection input widget. |
| `session_state` | v1-stable | Core state mapping and attribute proxy. |
| `slider` | v1-stable | Core numeric input widget. |
| `spinner` | post-v1 experimental | Status grouping behavior may still tighten in v1.x. |
| `stop` | v1-stable | Flow-control helper that halts the current script pass. |
| `subheader` | v1-stable | Core text output. |
| `status` | post-v1 experimental | Status grouping behavior may still tighten in v1.x. |
| `success` | v1-stable | Core status output. |
| `table` | v1-stable | Static terminal table display. |
| `text` | v1-stable | Core text output. |
| `text_input` | v1-stable | Core input widget. |
| `title` | v1-stable | Core text output. |
| `toast` | post-v2 experimental | Transient terminal notification, new in v2.1.0. |
| `toggle` | post-v2 experimental | On/off switch with checkbox semantics, new in v2.1.0. |
| `warning` | v1-stable | Core status output. |
| `write` | v1-stable | Core text/value output. |
<!-- API_CLASSIFICATION_END -->

## Text and Status

`st.help` is post-v1 experimental while the terminal formatting and public name
settle. The other text helpers in this group are v1-stable.

```python
st.title(body, *, key=None) -> None
st.header(body, *, key=None) -> None
st.subheader(body, *, key=None) -> None
st.text(body) -> None
st.caption(body) -> None
st.markdown(body) -> None
st.code(body, language=None) -> None
st.write(*args) -> None
st.help(obj_or_text) -> None
```

```python
import stui as st

st.title("Release dashboard", key="page-title")
st.markdown("Track local jobs without opening a browser.")
st.write("active jobs =", 3)
```

```python
st.success(body) -> None
st.info(body) -> None
st.warning(body) -> None
st.error(body) -> None
st.exception(exc) -> None
st.status(label, state="running", expanded=False)
st.spinner(text="Working...")
```

`st.status` and `st.spinner` are post-v1 experimental while status grouping
behavior is tested in real terminal apps.

```python
try:
    raise RuntimeError("model failed")
except RuntimeError as exc:
    st.exception(exc)

with st.status("Indexing", state="running", expanded=True):
    st.write("Reading local files")

with st.spinner("Waiting for job"):
    st.write("Polling once")

st.help(st.progress)
```

`st.status` accepts `state="running"`, `"complete"`, or `"error"`. It returns a
context-manager object, renders a terminal status block, and can capture child
elements when used with `with`. Child elements are visible when
`expanded=True`; the default collapsed block keeps children grouped but hides
them from the visible TUI. `st.spinner` returns a simple static display/context
primitive; it does not animate, run background work, or expose a mutable update
object. `st.help` renders plain text directly or a simple signature and
docstring for Python objects; it is not a pager or object browser.

## Data Display

```python
st.json(obj) -> None
st.table(data, *, max_rows=None, max_cols=None) -> None
st.dataframe(data, *, max_rows=None, max_cols=None) -> None
st.metric(label, value, delta=None) -> None
st.progress(value, text=None) -> None
st.bar_chart(data, *, width=None, height=None) -> None
st.line_chart(data, *, width=None, height=None) -> None
st.divider() -> None
```

In v2.0.0, `st.json`, `st.progress`, `st.table`, `st.dataframe`, `st.metric`,
`st.bar_chart`, and `st.line_chart` are v1-stable static display primitives.
Tables support scalars, lists or tuples of scalars, lists or tuples of dicts,
lists or tuples of lists/tuples, dicts of scalar values, dicts of lists/tuples,
dataclass instances, namedtuple-like objects, simple objects with public
attributes, and pandas-like objects with `to_dict(orient="records")` and
`columns` attributes. Multiline table cells are normalized for terminal display.
`st.dataframe` is an alias for static table display; it does not add editing,
sorting, selection, or pandas as a required dependency.
Use `max_rows` and `max_cols` to cap static output; hidden rows or columns are
called out with visible `+N rows` or `+N cols` markers.

Charts are compact terminal summaries. `st.bar_chart` supports numeric scalars,
lists or tuples of numbers, dicts of numbers, simple `(label, value)` pairs,
simple lists of dicts, and dict-of-column shapes with a numeric `value`,
`score`, `count`, `total`, or `y` column. `st.line_chart` supports numeric
scalars, lists or tuples of numbers, dicts of numeric series, simple
`(label, value)` pairs, simple lists of dicts, and dict-of-column shapes with
numeric series. Non-finite values are ignored. Unsupported or all-invalid data
renders `No chart data`. Chart `width` and `height` values, when provided, must
be positive integers.

```python
import stui as st

st.metric("accuracy", "91.2%", delta="+1.8")
st.progress(0.6, text="training")
st.table([
    {"run": "baseline", "latency_ms": 42},
    {"run": "quantized", "latency_ms": 24},
])
st.bar_chart({"baseline": 42, "quantized": 24})
```

## Layout

`st.container`, `st.expander`, `st.columns`, `st.form`, and
`st.form_submit_button` are v1-stable. They are terminal grouping primitives,
not browser layout compatibility APIs.

```python
st.container()
st.columns(count)
st.expander(label, expanded=False, *, key=None)
st.form(key)
st.form_submit_button(
    label="Submit",
    *,
    disabled=False,
    on_click=None,
    args=None,
    kwargs=None,
) -> bool
```

Use layout helpers as context managers:

```python
import stui as st

with st.container():
    st.header("Inputs")
    name = st.text_input("Name")

left, right = st.columns(2)
with left:
    st.metric("Queued", 4)
with right:
    st.metric("Failed", 0)

with st.expander("Advanced", expanded=False, key="advanced"):
    dry_run = st.checkbox("Dry run", value=True)

with st.form("job-form"):
    batch = st.number_input("Batch size", min_value=1, value=8)
    submitted = st.form_submit_button("Queue job")

if submitted:
    st.success(f"Queued {name} with batch size {batch}")
```

`st.columns(count)` accepts a positive integer and returns that many context
managers. Columns render side-by-side when each column has enough terminal
width, then stack vertically on narrow terminals. It does not support browser
grid behavior, custom gaps, width ratios, tabs, sidebars, or horizontal
scrolling. See [Layout Primitives](layouts.md) for the current layout boundary.

## Widgets

All widget keys are strings or `None`. When `key` is omitted, `stui` generates a
stable key from the widget type, label, and call position.

Widget callbacks run after the changed value is committed to `st.session_state`.
Pass positional callback arguments with `args=(...)` and keyword callback
arguments with `kwargs={...}`.

```python
st.button(
    label,
    key=None,
    help=None,
    disabled=False,
    on_click=None,
    args=None,
    kwargs=None,
) -> bool
```

```python
if st.button("Refresh", key="refresh", help="Run the local refresh step"):
    st.info("Refresh requested")
```

```python
st.slider(
    label,
    min_value=0,
    max_value=100,
    value=None,
    step=1,
    *,
    key=None,
    help=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> int | float
```

```python
threshold = st.slider(
    "Threshold",
    0.0,
    1.0,
    value=0.5,
    step=0.1,
    key="threshold",
)
```

```python
st.text_input(
    label,
    value="",
    *,
    key=None,
    placeholder=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> str
```

```python
name = st.text_input("Run name", value="baseline", placeholder="baseline")
```

```python
st.checkbox(
    label,
    value=False,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> bool
```

```python
dry_run = st.checkbox("Dry run", value=True, key="dry-run")
```

```python
st.number_input(
    label,
    min_value=None,
    max_value=None,
    value=0,
    step=1,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> int | float
```

```python
batch_size = st.number_input("Batch size", min_value=1, max_value=128, value=16)
```

```python
st.selectbox(
    label,
    options,
    index=0,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
)
```

```python
model = st.selectbox("Model", ["tiny", "base", "large"], index=1)
```

```python
st.radio(
    label,
    options,
    index=0,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
)
```

```python
mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
```

`st.multiselect` is post-v2 experimental. It renders a checkbox-style option
list: arrow keys move the highlight, Space or Enter toggles the highlighted
option. It returns the selected options as a tuple kept in options order, and
stored selections that are no longer present in `options` are dropped on the
next run. `default` accepts a single option or a list of options.

```python
st.multiselect(
    label,
    options,
    default=None,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> tuple
```

```python
datasets = st.multiselect("Datasets", ["train", "val", "test"], default=["train"])
```

`st.toggle` is post-v2 experimental. It behaves exactly like `st.checkbox` but
renders as an on/off switch.

```python
st.toggle(
    label,
    value=False,
    *,
    key=None,
    disabled=False,
    on_change=None,
    args=None,
    kwargs=None,
) -> bool
```

```python
verbose = st.toggle("Verbose logs", value=False, key="verbose")
```

## Notifications

`st.toast` is post-v2 experimental. It queues a short transient notification
that appears in the terminal after the current script run renders, then
disappears on its own. Toasts are not part of the rendered element tree, so
`stui check` does not count them as visible elements, and a run that fails with
an error drops its queued toasts.

```python
st.toast(body) -> None
```

```python
if st.button("Save"):
    st.toast("Settings saved")
```

## Session State

```python
st.session_state[key]
st.session_state[key] = value
del st.session_state[key]
key in st.session_state
st.session_state.get(key, default=None)
st.session_state.items()
st.session_state.keys()
st.session_state.values()
st.session_state.name
st.session_state.name = value
```

```python
import stui as st

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write("count =", st.session_state.count)
```

## Flow Control

```python
st.rerun() -> None
st.stop() -> None
```

```python
if st.button("Reset"):
    st.session_state.count = 0
    st.rerun()

if "token" not in st.session_state:
    st.warning("Missing token")
    st.stop()
```

## CLI Validation

```bash
stui check APP.py
stui check APP.py --json
stui check APP.py --strict
stui check APP.py --strict --repeat 2
stui selftest
stui selftest --json
stui selftest --strict
stui selftest --strict --repeat 2
```

`stui check` runs a script through the `stui` runtime without launching the
interactive TUI. It exits `0` when the app renders without runtime errors,
`1` for script/runtime/API errors, and `2` for invalid script paths. The
`--json` payload includes `strict`, `warnings`, `summary.warning_count`,
`summary.runs_requested`, `summary.runs_completed`, `summary.total_element_count`,
and a `runs` list with per-pass element, warning, and error counts. In
`--strict` mode, authoring warnings such as a script that renders no visible
elements fail the check while keeping `error: null` and `status: "ok"` for
warning-only failures. Use `--repeat N` to run the script multiple times in one
runtime and catch repeat-run state or recovery issues.

`stui selftest --strict` is an installed-package/release gate. It validates
package metadata, bundled demo resources, all init templates, all bundled
examples, and doctor diagnostics without launching a full TUI. Use
`--repeat N` to repeat generated-template and bundled-example checks.

## v2.1 Stable Status

The signatures above are intentionally covered by tests in v2.1.0. The
classification table marks each top-level API as `v1-stable`,
`post-v1 experimental`, or `post-v2 experimental`; see
[API Stability](api-stability.md) for the full compatibility promise and
post-v1 deprecation policy.

v2.1.0 keeps the v1.4 through v2.0 stable APIs intact while adding new
experimental widgets on top of the v2 stable contract in
[v2 readiness](v2-readiness.md). Any change to stable names should be treated
as a compatibility event unless it fixes a correctness, terminal, or security
issue and is documented in the changelog and release notes.

These APIs stay experimental in v2.1.0 and remain outside the v2 stable
contract:

- Help and status: `st.help`, `st.status`, and `st.spinner` formatting and
  grouping behavior (post-v1 experimental).
- New in v2.1.0: `st.multiselect`, `st.toggle`, and `st.toast`
  (post-v2 experimental).

APIs and feature areas explicitly deferred from the v1 stable surface are
listed in [API Stability](api-stability.md#deferred-for-v1). They include
`st.sidebar`, `st.tabs`, `st.file_uploader`, `st.cache_data`,
`st.cache_resource`, `st.components`, `st.empty`, editable dataframes,
plotting-library parity, custom column ratios/gaps, browser/server runtime,
websocket, or port-forwarding runtime.
