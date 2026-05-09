# stui v0.1.0rc2

`stui` is a tiny Streamlit-inspired terminal UI experiment for Python. It lets
you write small top-to-bottom Python scripts with familiar calls like
`st.title`, `st.slider`, `st.button`, and `st.session_state`, then render them
as a Textual TUI in the terminal.

This release candidate prepares the project for safe TestPyPI/PyPI publishing by
renaming the distribution to `stui-terminal` while keeping the import package
and console command as `stui`. It is not a real PyPI publish action.

`stui` is not official Streamlit, is not affiliated with Streamlit, and does not
aim for full Streamlit compatibility.

## What Changed Since v0.1.0rc1

- Documented the future PyPI install command:

```bash
python3.11 -m pip install stui-terminal
```

- Clarified the package naming boundary:
  - PyPI distribution: `stui-terminal`
  - Python import package: `stui`
  - CLI command: `stui`
- Kept editable source installs documented for local development:
- Added a Trusted Publishing GitHub Actions workflow for future TestPyPI/PyPI
  publication.
- Added publishing setup documentation for TestPyPI first.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python3.11 -m pip install -e ".[dev]"
```

## Install

When published to PyPI:

```bash
python3.11 -m pip install stui-terminal
```

Use the public API as:

```python
import stui as st
```

Run an example from a source checkout:

```bash
stui run examples/basic.py
stui run examples/counter.py
stui run examples/model_demo.py
```

## Known Limitations

- No charts yet
- No dataframes or tables yet
- No columns, sidebar, layouts, forms, caching, or file upload
- Slider supports numeric values only
- `text_input` reruns on submit, not every keystroke
- Linear layout only
- Pre-1.0 API, so compatibility is not guaranteed yet

## Verification

Local verification required after this documentation change:

```bash
python3.11 -m pytest
```

Expected full release-candidate verification:

```bash
python -m pip install -e ".[dev]"
ruff check .
python -m pytest
python -m build
python -m twine check dist/*
stui --version
python -m stui --version
```

## Repository

GitHub: https://github.com/marmar9615-cloud/stui-terminal
