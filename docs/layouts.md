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
enough for readable columns; otherwise they stack vertically. Nested columns use
their parent column width for that decision, so an inner column group may stack
even when the outer group still renders side-by-side.

Recommended patterns:

- Use two or three columns for compact summaries, metrics, and short controls.
- Use `st.container()` for section grouping when side-by-side display is not
  important.
- Use `st.expander(..., key="stable-key")` for optional details, especially in
  repeated sections.
- Put wide tables or long text outside columns when possible; they are easier to
  read in the full terminal width.
- Avoid deep nested columns. They are supported modestly, but narrow terminals
  will stack them quickly.

Limitations:

- No width ratios or weighted specifications.
- No configurable gaps, vertical alignment, or horizontal scrolling.
- No sidebar, browser grid, or arbitrary responsive layout engine.
- Nested grouping is supported, but deeply nested columns are discouraged
  because narrow terminals will quickly become hard to read.
- Column layout is stable for integer-count columns, but intentionally modest:
  no custom ratios, gaps, sidebars, tabs, or browser-grid behavior yet.

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

The v2.2 evaluation did not add `st.tabs`. In the current top-to-bottom script
and element model, both tab bodies would execute even if only one were visible.
Shipping that behavior without a stronger contract could hide errors or side
effects, destabilize generated widget keys, and make nested forms/containers
and focus restoration surprising. Multiline input, caching, and multi-file
watch correctness took priority over introducing that ambiguity.

Concrete criteria before revisiting tabs:

- Keyboard navigation is predictable in local terminals and SSH/headless-style
  sessions.
- Hidden tab content does not surprise users by preserving or losing widget
  values differently from visible content.
- Generated widget keys remain stable when tabs are reordered or toggled.
- Nested tabs either have deterministic behavior or fail with an explicit,
  readable usage error.
- Forms, columns, and expanders containing tab groups preserve their existing
  state and render-order contracts.
- Narrow terminals expose a discoverable keyboard path without clipping the tab
  labels or trapping focus.
- The API remains small and does not imply Streamlit compatibility.
