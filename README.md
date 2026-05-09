# stui

[![CI](https://github.com/marmar9615-cloud/stui-terminal/actions/workflows/ci.yml/badge.svg)](https://github.com/marmar9615-cloud/stui-terminal/actions/workflows/ci.yml)

`stui` is a tiny Streamlit-inspired framework for building terminal-native
Python apps. Write a short script, run it in your terminal, and get a Textual UI
with stateful controls.

It is built for local tools, demos, data scripts, model debug panels, SSH
sessions, and headless environments where opening a browser, binding a port, or
running a dashboard server is unnecessary ceremony. The public API is
deliberately small and readable.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer. The API intentionally feels familiar, but this
project keeps its own smaller surface area.

## Preview

![stui model demo terminal screenshot](assets/model_demo.svg)

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

Install the PyPI distribution named `stui-terminal`:

```bash
python -m pip install stui-terminal
```

The PyPI distribution name is `stui-terminal`, but the import package and CLI
are both `stui`:

```python
import stui as st
```

For local development from a checkout, use an editable install with the dev
extra:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

For runtime-only local use, install without the dev extra:

```bash
python -m pip install -e .
```

## 60-Second Quickstart

Create a file named `app.py`:

```python
import stui as st

st.title("Hello from the terminal")

name = st.text_input("Name", "MarMar")
level = st.slider("Level", 1, 10, 5)

if st.button("Greet"):
    st.success(f"Hi {name}. Level {level} selected.")
```

Install and run it:

```bash
python -m pip install stui-terminal
stui run app.py
```

If the `stui` command is not on your `PATH`, use the module entry point:

```bash
python -m stui run app.py
```

## Build Your First App

`stui` scripts rerun when users interact with widgets. Use
`st.session_state` for values that should survive reruns:

```python
import stui as st

st.title("Counter")

if "count" not in st.session_state:
    st.session_state.count = 0

step = st.slider("Step", 1, 10, 1)

if st.button("Add"):
    st.session_state.count += step

if st.button("Reset"):
    st.session_state.count = 0

st.write("count =", st.session_state.count)
```

Run it with:

```bash
stui run app.py
```

Start from the included examples when you want a larger reference:

```bash
stui run examples/counter.py
stui run examples/inputs.py
stui run examples/data_display.py
stui run examples/dashboard.py
```

## Copy-Paste Examples

### Slider and Button

```python
import stui as st

st.title("Slider and Button")

if "runs" not in st.session_state:
    st.session_state.runs = 0

threshold = st.slider("Threshold", 0.0, 1.0, 0.5, step=0.1)

if st.button("Run"):
    st.session_state.runs += 1
    st.success(f"Run {st.session_state.runs} at threshold {threshold}")
```

### Inputs

```python
import stui as st

st.title("Inputs")

name = st.text_input("Name", "MarMar")
batch = st.number_input("Batch size", min_value=1, max_value=128, value=16)
model = st.selectbox("Model", ["tiny", "base", "large"], index=1)
mode = st.radio("Mode", ["fast", "balanced", "careful"], index=1)
dry_run = st.checkbox("Dry run", value=True)

st.write("name =", name)
st.write("batch =", batch)
st.write("model =", model)
st.write("mode =", mode)
st.write("dry run =", dry_run)
```

### Table and Dataframe

```python
import stui as st

st.title("Runs")

rows = [
    {"name": "baseline", "accuracy": 0.81, "latency_ms": 42},
    {"name": "quantized", "accuracy": 0.79, "latency_ms": 24},
    {"name": "distilled", "accuracy": 0.77, "latency_ms": 18},
]

st.table(rows)
st.dataframe({"setting": ["device", "batch"], "value": ["cpu", 16]})
```

### Progress and Status

```python
import stui as st

st.title("Job Status")

complete = st.slider("Complete", 0, 100, 35)
st.progress(complete, text="current job")

if complete == 100:
    st.success("Done")
elif complete >= 75:
    st.warning("Almost there")
else:
    st.info("Running")
```

## Why terminal-native?

Some useful Python apps do not need a browser runtime. `stui` keeps the
interface inside the terminal so it can fit naturally into:

- SSH sessions, remote machines, and headless boxes.
- Internal tools where opening ports or managing local server URLs is friction.
- Offline or locked-down environments where browser access is limited.
- Model, data, and DevOps workflows that already start from a shell.

That also keeps the boundary simple: `stui` does not start a web server, use
websockets, require port-forwarding, or depend on Streamlit at runtime.

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

# List installed examples and print environment diagnostics.
stui examples
stui doctor

# Run the test suite.
python3.11 -m pytest
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

Import the API as:

```python
import stui as st
```

The public API is intentionally compact:

- Text: `st.title`, `st.header`, `st.subheader`, `st.caption`, `st.text`,
  `st.markdown`, `st.write`, `st.divider`
- Status: `st.info`, `st.success`, `st.warning`, `st.error`, `st.exception`
- Display: `st.code`, `st.json`, `st.progress`, `st.table`, `st.dataframe`
- Inputs: `st.button`, `st.slider`, `st.text_input`, `st.checkbox`,
  `st.number_input`, `st.selectbox`, `st.radio`
- State and control flow: `st.session_state`, `st.rerun`

Inputs support stable `key` values and optional callbacks where the function
signature documents them. Tables are simple static displays and do not require
pandas.

## Compatibility

`stui` is Streamlit-inspired, not Streamlit-compatible. Existing Streamlit apps
usually need small edits before they run in `stui`; unsupported calls should be
removed or replaced with the compact API above.

Runtime expectations:

- Python 3.11 or newer.
- Terminal UI powered by Textual and Rich.
- No Streamlit runtime dependency.
- No browser tab, local web server, websocket, or port-forwarding flow.
- Static table/dataframe display without dataframe editing, sorting, or charts.

## Common Mistakes

- Installing `stui` instead of `stui-terminal`. The PyPI package is
  `stui-terminal`; the import and CLI are `stui`.
- Running `stui run` from a different Python environment than the one where the
  package was installed. Try `python -m stui run app.py`.
- Expecting a browser dashboard. `stui` renders inside your terminal.
- Reusing Streamlit-only APIs such as forms, columns, sidebars, charts, file
  upload, or caching decorators. They are not part of this MVP API.
- Doing slow network or model work at top level. Scripts rerun after
  interactions, so keep top-level work light and cache expensive work yourself.
- Forgetting stable `key` values when creating similar widgets in loops.

## Troubleshooting

### `stui: command not found`

Make sure you installed into the same Python environment that your shell is
using:

```bash
python -m pip install stui-terminal
python -m stui --version
```

If `python -m stui --version` works but `stui --version` does not, your
environment's script directory is not on `PATH`. Running through
`python -m stui ...` is a reliable workaround.

### Python Version

`stui` requires Python 3.11 or newer:

```bash
python --version
```

If that prints an older version, create a 3.11+ environment first:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install stui-terminal
```

### Terminal Rendering

`stui` renders a Textual app inside your terminal. For the best results, use a
modern terminal with UTF-8 and color support. If borders, focus rings, or block
characters look wrong, try another terminal app, make the window wider, and
check that `TERM` is set to a normal interactive terminal value such as
`xterm-256color`.

### macOS Editable Install Quirk

If a local editable install appears to succeed but `import stui` or
`stui --version` cannot find the package on macOS, check whether the virtual
environment or editable-install `.pth` file was marked hidden:

```bash
chflags -R nohidden .venv
python -m pip install -e ".[dev]"
python -m stui --version
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

### Inputs

`examples/inputs.py` shows text, numeric, selectbox, radio, checkbox, and button
controls together.

```bash
stui run examples/inputs.py
```

### Data Display

`examples/data_display.py` shows tables, JSON, and code output.

```bash
stui run examples/data_display.py
```

### Dashboard

`examples/dashboard.py` combines controls, progress, status messages, and a
small table into a compact terminal control panel.

```bash
stui run examples/dashboard.py
```

### Kitchen Sink

`examples/kitchen_sink.py` exercises the stable 0.2.x API surface in one
compact app.

```bash
stui run examples/kitchen_sink.py
```

## Limitations

- No browser, web server, websocket, or port-forwarding runtime.
- No Streamlit dependency and no promise of Streamlit compatibility.
- No charts, forms, columns, sidebars, or file upload yet.
- Tables are static display only; there is no full dataframe editing or sorting.
- Slider input supports numeric values only.
- Layout is currently linear and script-driven.
- The app reruns the script as interactions change state, so examples should keep top-level work lightweight.
- Error handling is still early and meant for development feedback.
- The package is an MVP and has not stabilized a long-term compatibility policy.

## Roadmap

- Add charts and richer dataframe display.
- Add simple form-like batching once rerun semantics are clearer.
- Improve focus behavior, accessibility hints, and keyboard discoverability.
- Expand example coverage for data scripts, model controls, DevOps panels, and internal tools.
- Keep the implementation clean-room, readable, and based on Textual first-party widgets where possible.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the local development workflow and
project boundaries.
