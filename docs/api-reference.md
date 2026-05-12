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

These names are intentionally exported from `stui.__all__`:

```text
__version__
button
bar_chart
caption
checkbox
code
container
dataframe
divider
error
exception
expander
form
form_submit_button
header
info
json
line_chart
markdown
metric
number_input
progress
radio
rerun
selectbox
session_state
slider
stop
subheader
success
table
text
text_input
title
warning
write
```

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
```

```python
try:
    raise RuntimeError("model failed")
except RuntimeError as exc:
    st.exception(exc)
```

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

with st.expander("Advanced", expanded=False, key="advanced"):
    dry_run = st.checkbox("Dry run", value=True)

with st.form("job-form"):
    batch = st.number_input("Batch size", min_value=1, value=8)
    submitted = st.form_submit_button("Queue job")

if submitted:
    st.success(f"Queued {name} with batch size {batch}")
```

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

The signatures above are intentionally covered by tests in v0.6.0. Treat them
as stable candidates on the path to v1, not as a final v1 compatibility promise.
Behavior can still tighten before v1 when a bug fix, terminal limitation, or
clearer API boundary requires it.

These areas need the most feedback before they can be called v1-stable:

- Forms: deferred submit behavior and callback timing.
- Grouping: `st.container` and `st.expander` as terminal grouping primitives,
  not a full layout engine.
- Data display: static `st.table` and `st.dataframe` without editing/sorting.
- Charts: compact terminal summaries from `st.metric`, `st.bar_chart`, and
  `st.line_chart`, not plotting-library replacements.
- Flow control: clear expectations for `st.rerun` and `st.stop` in real apps.
