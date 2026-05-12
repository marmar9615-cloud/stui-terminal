# Layout Primitives

`stui` keeps layout terminal-native and modest. The current public primitives
are for grouping readable terminal output, not for recreating browser grid or
Streamlit layout compatibility.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Current Primitives

### `st.container()`

Use `st.container()` as a context manager when a section should stay visually
grouped in the terminal.

```python
with st.container():
    st.subheader("Overview")
    st.write("status =", "ready")
```

Containers preserve child order and can contain other grouping primitives.

### `st.columns(count)`

Use `st.columns(count)` for small side-by-side sections:

```python
left, right = st.columns(2)

with left:
    st.metric("Queued", 4)

with right:
    st.metric("Failed", 0)
```

The `count` argument must be a positive integer. Each returned value is a
context manager. Columns render side-by-side only when the terminal is wide
enough for readable columns; otherwise they stack vertically.

Limitations:

- No width ratios or weighted specifications.
- No configurable gaps, vertical alignment, or horizontal scrolling.
- No sidebar, browser grid, or arbitrary responsive layout engine.
- Nested grouping is supported, but deeply nested columns are discouraged
  because narrow terminals will quickly become hard to read.
- Column layout is pre-v1 experimental and may tighten based on terminal
  compatibility feedback.

### `st.expander(label, expanded=False, key=None)`

Use `st.expander(...)` as a context manager for content that can be collapsed.
In the Textual app, a focused expander toggles with Enter or Space and stores
state in `st.session_state` under the explicit or generated key.

```python
with st.expander("Advanced", expanded=False, key="advanced"):
    st.checkbox("Dry run", value=True)
```

## Tabs

Tabs are deferred. A terminal tab API needs stable focus behavior, clear
keyboard affordances, and predictable state retention before it belongs in the
public surface. For now, use headings, containers, columns, or expanders to
organize sections.

Concrete criteria before revisiting tabs:

- Keyboard navigation is predictable in local terminals and SSH/headless-style
  sessions.
- Hidden tab content does not surprise users by preserving or losing widget
  values differently from visible content.
- Generated widget keys remain stable when tabs are reordered or toggled.
- The API remains small and does not imply Streamlit compatibility.
