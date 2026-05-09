# stui

[![CI](https://github.com/marmar9615-cloud/stui-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/marmar9615-cloud/stui-terminal/actions/workflows/ci.yml)

`stui` is a tiny Streamlit-inspired framework for terminal-native Python apps:
write a short Python script, run it in your terminal, and get a Textual UI with
stateful controls.

It is built for local tools, demos, data scripts, model debug panels, SSH
sessions, and headless environments where a browser dashboard is more ceremony
than help. The public API is deliberately small and readable.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer. The API intentionally feels familiar, but this
project keeps its own smaller surface area.

## Preview

```text
┌─ stui ───────────────────────────────────────────┐
│ stui demo                                        │
│                                                  │
│ x                                                │
│ [██░░░░░░░░░░░░] 10                              │
│                                                  │
│ [ Increment ]                                    │
│                                                  │
│ x = 10                                           │
│ count = 0                                        │
│                                                  │
│ q Quit   r Rerun   tab Focus next                │
└──────────────────────────────────────────────────┘
```

## Install

Use Python 3.11 or newer.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python3.11 -m pip install -e ".[dev]"
```

For runtime-only local use, install without the dev extra:

```bash
python3.11 -m pip install -e .
```

## Quickstart

Set up the project and run the basic example:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
stui run examples/basic.py
```

You can also run through the module entry point:

```bash
python3.11 -m stui run examples/counter.py
```

Scripts use the public `stui` API:

```python
import stui as st

st.title("stui demo")

if "count" not in st.session_state:
    st.session_state.count = 0

value = st.slider("value", 0, 100, 25)

if st.button("Increment"):
    st.session_state.count += 1

st.write("value =", value)
st.write("count =", st.session_state.count)
```

More examples:

```bash
stui run examples/counter.py
stui run examples/model_demo.py
```

## Commands

```bash
# Install the project for local development.
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"

# Run the smoke-size example app.
stui run examples/basic.py

# Run the stateful counter example.
stui run examples/counter.py

# Run the deterministic model-parameter demo.
stui run examples/model_demo.py

# Run the test suite.
python -m pytest
```

## Keyboard Shortcuts

- `q`: quit the app
- `r`: rerun the script
- `tab`: focus the next widget
- `enter`: press the focused button
- `left` or `h`: decrease the focused slider
- `right` or `l`: increase the focused slider
- `home`: set the focused slider to its minimum value
- `end`: set the focused slider to its maximum value

## Current API

The current public API is intentionally small:

- `st.title(body, *, key=None)`: render a title.
- `st.header(body, *, key=None)`: render a section header.
- `st.text(body)`: render plain text.
- `st.markdown(body)`: render Markdown-flavored text.
- `st.divider()`: render a horizontal divider.
- `st.info(body)`, `st.success(body)`, `st.warning(body)`, `st.error(body)`: render status messages.
- `st.write(*args)`: render simple text output.
- `st.button(label, key=None, help=None, disabled=False, on_click=None, args=None, kwargs=None)`: render a button and return `True` for the run where it was pressed.
- `st.slider(label, min_value=0, max_value=100, value=None, step=1, *, key=None, help=None, disabled=False, on_change=None, args=None, kwargs=None)`: render a numeric slider and return its current value.
- `st.text_input(label, value="", *, key=None, placeholder=None, disabled=False, on_change=None, args=None, kwargs=None)`: render a single-line text input and return its current value.
- `st.checkbox(label, value=False, *, key=None, disabled=False, on_change=None, args=None, kwargs=None)`: render a checkbox and return its current value.
- `st.session_state`: persist values across reruns with dict-style or attribute-style access.
- `st.rerun()`: request a script rerun.

Import the API as:

```python
import stui as st
```

## Examples

### Counter

`examples/counter.py` shows a minimal stateful app with increment, decrement, and
reset controls.

```bash
stui run examples/counter.py
```

### Model Demo

`examples/model_demo.py` shows a small model-parameter playground using text
input, checkbox, sliders, status messages, session state, and deterministic
scoring. It is intentionally local and fake: there are no network calls or model
dependencies.

```bash
stui run examples/model_demo.py
```

## Limitations

- No browser, web server, websocket, or port-forwarding runtime.
- No Streamlit dependency and no promise of Streamlit compatibility.
- No charts, tables, dataframes, forms, columns, sidebars, or file upload yet.
- Slider input supports numeric values only.
- Layout is currently linear and script-driven.
- The app reruns the script as interactions change state, so examples should keep top-level work lightweight.
- Error handling is still early and meant for development feedback.
- The package is an MVP and has not stabilized a long-term compatibility policy.

## Roadmap

- Add small text output helpers such as `caption`.
- Add common controls such as `selectbox`, `radio`, and number inputs.
- Add simple display primitives for tables and progress.
- Improve focus behavior, accessibility hints, and keyboard discoverability.
- Expand example coverage for data scripts, model controls, DevOps panels, and internal tools.
- Keep the implementation clean-room, readable, and based on Textual first-party widgets where possible.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local development workflow and
project boundaries.
