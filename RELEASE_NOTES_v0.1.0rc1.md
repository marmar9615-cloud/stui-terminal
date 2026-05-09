# stui v0.1.0rc1

`stui` is a tiny Streamlit-inspired terminal UI experiment for Python. It lets
you write small top-to-bottom Python scripts with familiar calls like
`st.title`, `st.slider`, `st.button`, and `st.session_state`, then render them
as a Textual TUI in the terminal.

This is an early release candidate. It is not official Streamlit, is not
affiliated with Streamlit, and does not aim for full Streamlit compatibility.

## Highlights

- Terminal-native app runner: `stui run path/to/app.py`
- Module entrypoint: `python -m stui run path/to/app.py`
- Top-to-bottom script reruns on widget interaction
- Persistent `st.session_state` with dict and attribute access
- Public APIs for:
  - `title`, `header`, `text`, `markdown`, `write`, `divider`
  - `button`, `slider`, `text_input`, `checkbox`
  - `success`, `info`, `warning`, `error`
  - `rerun`
- Clean-room Textual slider widget with keyboard support
- Readable terminal traceback panels for script errors
- Example apps for a basic counter-style demo, counter controls, and local model settings

## Install For Local Development

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run an example:

```bash
stui run examples/basic.py
stui run examples/counter.py
stui run examples/model_demo.py
```

## Why Terminal-Native?

Some Python prototypes and internal tools do not need a browser, a local web
server, or port forwarding. `stui` is meant for quick local tools, SSH sessions,
headless boxes, model/debug panels, and small scripts where the terminal is
already the natural workspace.

## Known Limitations

- No charts yet
- No dataframes or tables yet
- No columns, sidebar, layouts, forms, caching, or file upload
- Slider supports numeric values only
- `text_input` reruns on submit, not every keystroke
- Linear layout only
- Pre-1.0 API, so compatibility is not guaranteed yet

## Verification

Local verification before this release candidate:

```bash
python -m pip install -e ".[dev]"
ruff check .
python -m pytest
python -m build
python -m twine check dist/*
stui --version
python -m stui --version
```

Results:

- Tests: `55 passed`
- Ruff: passed
- Build: passed
- Twine check: passed for sdist and wheel
- GitHub Actions CI: passed on Python 3.11 and 3.12

## Repository

GitHub: https://github.com/marmar9615-cloud/stui-terminal
