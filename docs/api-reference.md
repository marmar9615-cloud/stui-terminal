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
| `bar_chart` | pre-v1 experimental | Terminal chart rendering may still tighten before v1. |
| `button` | v1-stable | Core input widget. |
| `caption` | v1-stable | Core text output. |
| `checkbox` | v1-stable | Core input widget. |
| `code` | v1-stable | Core text output. |
| `columns` | pre-v1 experimental | Responsive terminal layout behavior may still tighten. |
| `container` | pre-v1 experimental | Terminal grouping primitive, not a full layout engine. |
| `dataframe` | pre-v1 experimental | Static terminal display; editing and sorting are out of scope. |
| `divider` | v1-stable | Core visual separator. |
| `error` | v1-stable | Core status output. |
| `exception` | v1-stable | Core status output for exceptions. |
| `expander` | pre-v1 experimental | Terminal grouping behavior may still tighten. |
| `form` | pre-v1 experimental | Deferred submit behavior and callback timing need v1 feedback. |
| `form_submit_button` | pre-v1 experimental | Coupled to experimental form semantics. |
| `header` | v1-stable | Core text output. |
| `help` | pre-v1 experimental | Help formatting and the public name need v1 feedback. |
| `info` | v1-stable | Core status output. |
| `json` | pre-v1 experimental | Static terminal display formatting may change. |
| `line_chart` | pre-v1 experimental | Terminal chart rendering may still tighten before v1. |
| `markdown` | v1-stable | Core text output. |
| `metric` | pre-v1 experimental | Compact terminal summary formatting may change. |
| `number_input` | pre-v1 experimental | Newer input widget still gathering feedback. |
| `progress` | pre-v1 experimental | Terminal rendering and normalization may still tighten. |
| `radio` | pre-v1 experimental | Newer selection widget still gathering feedback. |
| `rerun` | pre-v1 experimental | Flow-control semantics need real-app feedback. |
| `selectbox` | pre-v1 experimental | Newer selection widget still gathering feedback. |
| `session_state` | v1-stable | Core state mapping and attribute proxy. |
| `slider` | v1-stable | Core numeric input widget. |
| `spinner` | pre-v1 experimental | Status grouping behavior may still tighten before v1. |
| `stop` | pre-v1 experimental | Flow-control semantics need real-app feedback. |
| `subheader` | v1-stable | Core text output. |
| `status` | pre-v1 experimental | Status grouping behavior may still tighten before v1. |
| `success` | v1-stable | Core status output. |
| `table` | pre-v1 experimental | Static terminal display formatting may change. |
| `text` | v1-stable | Core text output. |
| `text_input` | v1-stable | Core input widget. |
| `title` | v1-stable | Core text output. |
| `warning` | v1-stable | Core status output. |
| `write` | v1-stable | Core text/value output. |
<!-- API_CLASSIFICATION_END -->

## Text and Status

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

```python
try:
    raise RuntimeError("model failed")
except RuntimeError as exc:
    st.exception(exc)

with st.status("Indexing", state="running"):
    st.write("Reading local files")

with st.spinner("Waiting for job"):
    st.write("Polling once")

st.help(st.progress)
```

`st.status` accepts `state="running"`, `"complete"`, or `"error"`. It renders a
terminal status block and can group child elements when used as a context
manager. `st.spinner` is a simple display/context primitive; it does not animate
or update after the script pass completes. `st.help` renders plain text directly
or a simple signature and docstring for Python objects.

## Data Display

```python
st.json(obj) -> None
st.table(data) -> None
st.dataframe(data) -> None
st.metric(label, value, delta=None) -> None
st.progress(value, text=None) -> None
st.bar_chart(data, *, width=None, height=None) -> None
st.line_chart(data, *, width=None, height=None) -> None
st.divider() -> None
```

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

## Stability Before v1

The signatures above are intentionally covered by tests in v0.7.0. The
classification table marks each top-level API as either `v1-stable` or
`pre-v1 experimental`; see [API Stability](api-stability.md) for the full
compatibility promise before v1.0.0 and the post-v1 deprecation policy.

These areas need the most feedback before they can be called v1-stable:

- Forms: deferred submit behavior and callback timing.
- Grouping: `st.container`, `st.columns`, and `st.expander` as terminal
  grouping primitives, not a full layout engine.
- Data display: static `st.table` and `st.dataframe` without editing/sorting.
- Charts: compact terminal summaries from `st.metric`, `st.bar_chart`, and
  `st.line_chart`, not plotting-library replacements.
- Help and status: `st.help`, `st.status`, and `st.spinner` formatting and
  grouping behavior.
- Flow control: clear expectations for `st.rerun` and `st.stop` in real apps.
