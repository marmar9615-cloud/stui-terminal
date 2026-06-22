# stui v0.9.0

`stui` v0.9.0 is the final pre-v1 candidate closeout release on the path to
v1.0.0.

This is not the v1 launch and not a Streamlit compatibility promise. Public
launch-style X/LinkedIn copy remains saved for v1.0.0, after the stable API,
PyPI install path, examples, docs, CI, and terminal compatibility checks are
verified together.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- Freezes the documented top-level API list as the v1 candidate surface.
- Keeps stable versus pre-v1 experimental API labels explicit in the README,
  API reference, API stability docs, and v1 readiness docs.
- Documents deferred v1 feature areas such as sidebars, tabs, file upload,
  caching decorators, browser components, editable dataframes, plotting-library
  parity, custom column ratios/gaps, and browser/server/websocket runtimes.
- Keeps remaining v1 gates focused on terminal compatibility evidence,
  narrow-rendering documentation or fixes, package verification, release
  candidate checks, and changelog/release-note alignment.
- Refreshes quickstart, first-app, CLI, terminal compatibility, examples/init,
  limitations, non-goals, release checklist, and roadmap wording for the final
  v1-candidate docs pass.

## API Status

The v0.9.0 API surface is still pre-1.0, but it is the v1 candidate freeze. No
new feature work should enter this line unless it directly fixes or documents a
release blocker.

Stable-candidate areas include:

- Text output: `st.title`, `st.header`, `st.subheader`, `st.caption`,
  `st.text`, `st.markdown`, `st.write`, `st.divider`, and `st.code`.
- Basic status output: `st.info`, `st.success`, `st.warning`, `st.error`, and
  `st.exception`.
- Core inputs: `st.button`, `st.slider`, `st.text_input`, and `st.checkbox`.
- Core state: `st.session_state`.
- Package metadata: `st.__version__`.
- CLI commands documented for v1: `stui run`, `stui examples`,
  `stui example list`, `stui example copy`, `stui init`, `stui doctor`,
  `stui doctor --json`, and `stui --version`.

Pre-v1 experimental areas remain public but not stable:

- `st.status`, `st.spinner`, and `st.help` as terminal status/help primitives.
- `st.json`, `st.progress`, `st.table`, and `st.dataframe` as static display
  helpers with visible limits.
- `st.number_input`, `st.selectbox`, and `st.radio` as newer input widgets.
- `st.form` and `st.form_submit_button` while submit semantics and callback
  timing gather feedback.
- `st.container`, `st.columns`, and `st.expander` as terminal grouping helpers.
- `st.metric`, `st.bar_chart`, and `st.line_chart` as compact terminal
  summaries, not plotting-library replacements.
- `st.rerun` and `st.stop` while real-app flow-control semantics gather
  feedback.

## Remaining v1 Gates

- Capture final terminal compatibility evidence for macOS, Linux, container or
  SSH/headless-style workflows, narrow terminals, and wide terminals.
- Fix or document narrow-rendering issues for tables, charts, forms, expanders,
  and long labels.
- Verify clean installs and example flows from built wheel/source artifacts.
- Run release-candidate checks against the package that will be published.
- Keep README, changelog, release notes, roadmap, feedback docs, API reference,
  and v1 readiness docs aligned.

## CLI And Package Contract

Install from PyPI with:

```bash
python -m pip install stui-terminal
```

The distribution name remains `stui-terminal`; the import package and CLI
remain `stui`.

The v1 candidate command surface is:

```bash
stui run app.py
python -m stui run app.py
stui examples
stui example list
stui example copy counter ./counter.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
stui init ./forms_app.py --template forms
stui doctor
stui doctor --json
stui --version
```

Installed-package example/init/copy flows should work without cloning the
repository. The documented starter templates are `basic`, `dashboard`, and
`forms`.

## Terminal Compatibility

v0.9.0 remains evidence-driven. Common modern terminals are expected targets,
but unknown terminals should stay labeled test-needed until verified. Final v1
notes should include the tested OS, terminal emulator, shell, Python version,
`stui` version, install method, `TERM`, `COLORTERM`, `TERM_PROGRAM`, terminal
size, local/SSH/container/headless status, and `stui doctor` output.

## Verification

Before publishing v0.9.0, run:

```bash
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
```

Also verify representative installed-package flows:

```bash
stui --version
python -m stui --version
stui doctor
stui doctor --json
stui examples
stui example list
stui example copy basic ./basic.py
stui init ./new_app.py
stui init ./forms_app.py --template forms
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
