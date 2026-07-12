# Tabs

`st.tabs` is a post-v2 experimental layout API for switching between groups of
terminal content. `stui` is Streamlit-inspired, but it is not a Streamlit
compatibility layer and does not depend on Streamlit at runtime.

```python
import stui as st

overview, details = st.tabs(
    ["Overview", "Details"],
    key="workspace-tabs",
    default=0,
)

with overview:
    st.metric("Jobs", 12)

with details:
    st.text_input("Owner", key="owner")
```

## Execution And Rendering

Every tab context block executes on every normal top-to-bottom script pass.
Only the active block's elements are mounted in the Textual widget tree. This
keeps hidden widgets out of keyboard focus and prevents them from receiving UI
events, but it does not skip Python work in inactive blocks.

Use the existing cache APIs when work shared by tab blocks is expensive. Do not
rely on tabs as a conditional-execution primitive.

## State And Callbacks

```python
st.tabs(
    labels,
    *,
    key=None,
    default=0,
    on_change=None,
    args=None,
    kwargs=None,
)
```

The active value is a zero-based integer index stored through the existing
widget state pipeline. `default` must be a valid index. An explicit `key` is
recommended when labels may change; generated keys are deterministic from the
ordered labels and call position.

`on_change` runs after the active index is committed and receives `args` and
`kwargs` like other stateful widgets. Inside `st.form`, the selected pane
changes immediately, while the session value and callback remain pending until
the form is submitted.

## Labels And Input

- `labels` must be a non-empty sequence of non-empty strings.
- Duplicate labels are supported and remain distinct by their ordered index.
- Markup is displayed literally. Terminal controls, tabs, and newlines are
  escaped before rendering.
- Long labels are clipped and the first-party Textual tab row scrolls to keep
  the active tab usable in narrow terminals.

## Navigation And Layout

Press `Tab` or `Shift+Tab` to enter or leave the tab row. While the row has
focus, `Left` and `Right` select tabs and wrap at either end. Mouse selection is
also supported.

Tabs may contain or be placed inside containers, columns, expanders, and forms.
Nested tabs use the same active-only mounting model and support independent,
persistent keys. Explicit keys are especially useful for nested groups.
