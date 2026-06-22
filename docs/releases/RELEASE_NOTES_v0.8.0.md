# stui v0.8.0

`stui` v0.8.0 is a release-candidate hardening release on the path to v1.0.0.

This is not the v1 launch and not a Streamlit compatibility promise. Public
launch-style X/LinkedIn copy is intentionally out of scope for this release
candidate. Public announcement pushes remain saved for v1.0.0, after the stable
API, PyPI install path, examples, docs, CI, and terminal compatibility checks
are verified together.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- Stable versus pre-v1 experimental API labels remain explicit in the README,
  API reference, API stability docs, and v1 readiness docs.
- README now links the working API reference, API stability labels, terminal
  compatibility matrix, and v1 readiness checklist from the quickstart path.
- Installed-package users now get a clearer hint if they try to run
  `stui run examples/<name>.py` from a directory that does not contain the repo
  examples folder: copy the bundled example first with `stui example copy`.
- CLI install/init/example docs now restate the distribution/import/command
  split: install `stui-terminal`, import `stui`, run `stui`, and fall back to
  `python -m stui` when the console script is not on `PATH`.
- CLI tests cover the installed-package example-copy hint.
- Publishing docs and v1 readiness docs now point at the v0.8.0 release line
  and keep v0.9.0 focused on final v1-candidate closeout.

## API Status

The v0.8.0 API surface is still pre-1.0. The documented public surface remains
the contract for this release, with explicit labels:

- `v1-stable` APIs should keep their name, call shape, return type, and basic
  behavior through the remaining 0.x releases unless a correctness, terminal,
  or security issue forces a change.
- `pre-v1 experimental` APIs are public enough to use, but can still tighten
  before v1.0.0 with release-note coverage.
- Internal modules and dataclasses remain private implementation details.

No public APIs were removed in v0.8.0.

Stable-candidate areas include:

- Text output: `st.title`, `st.header`, `st.subheader`, `st.caption`,
  `st.text`, `st.markdown`, `st.write`, `st.divider`, and `st.code`.
- Basic status output: `st.info`, `st.success`, `st.warning`, `st.error`, and
  `st.exception`.
- Core inputs: `st.button`, `st.slider`, `st.text_input`, and `st.checkbox`.
- Core state: `st.session_state`.
- CLI commands documented for v1: `stui run`, `stui examples`,
  `stui example list`, `stui example copy`, `stui init`, `stui doctor`,
  `stui doctor --json`, and `stui --version`.

Pre-v1 experimental areas include:

- `st.status`, `st.spinner`, and `st.help` as terminal status/help primitives.
- `st.json`, `st.progress`, `st.table`, and `st.dataframe` as static display
  helpers with visible limits.
- `st.number_input`, `st.selectbox`, and `st.radio` as newer input widgets.
- `st.form` and `st.form_submit_button` while submit semantics and callback
  timing gather feedback.
- `st.container`, `st.columns`, and `st.expander` as terminal grouping helpers.
  `st.columns` accepts an integer count and stacks on narrow terminals.
- `st.metric`, `st.bar_chart`, and `st.line_chart` as compact terminal
  summaries, not plotting-library replacements.
- `st.rerun` and `st.stop` while real-app flow-control semantics gather
  feedback.

## CLI And Package Contract

Install from PyPI with:

```bash
python -m pip install stui-terminal
```

Run apps with:

```bash
stui run app.py
python -m stui run app.py
```

Create or copy starter scripts with:

```bash
stui examples
stui example list
stui example copy counter ./counter.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
```

The documented starter templates are `basic`, `dashboard`, and `forms`.

## Verification

Before publishing v0.8.0, run:

```bash
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
```

Also verify representative installed-package flows:

```bash
stui --version
stui doctor
stui doctor --json
stui examples
stui example list
stui example copy basic ./basic.py
stui init ./new_app.py
python -m stui run ./basic.py
python -m stui run ./new_app.py
```

For a docs-only sub-agent pass, `python3.11 -m pytest` is still required after
changes. The build, Twine, package install, tag, and publishing checks are
release-manager gates unless explicitly coordinated.

## Boundaries

- No browser runtime.
- No local web server, websocket, or port-forwarding flow.
- No Streamlit runtime dependency.
- No claim of Streamlit compatibility.
- No copied GPL slider code or `textual-slider` dependency.
- No X, LinkedIn, or other social launch copy for this pre-1.0 release.
- Public announcement push remains saved for v1.0.0.
