# stui v1.3.0

`stui` v1.3.0 is a professionalization and trust release for
`stui-terminal`, the PyPI package that provides the `stui` import package and
the `stui` CLI.

This release keeps the package/import/CLI contract intact:

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

`stui` remains Streamlit-inspired, not official Streamlit, not affiliated with
Streamlit, and not a Streamlit compatibility layer. It still does not add a
browser, local server, websocket runtime, port-forwarding flow, Streamlit
runtime dependency, `textual-slider`, pandas, or heavy plotting dependency.

## What Changed

v1.3.0 focuses on trust, package hygiene, installed-user validation, and docs
organization:

- Added `stui selftest` and `stui selftest --json`.
- Added `scripts/audit_package_contents.py` for release artifact hygiene.
- Added `docs/README.md` as a docs index.
- Added `model_demo` to `stui demo` so the README/PyPI screenshot can be run
  directly from an installed package.
- Kept stale announcement drafts out of source distributions.
- Removed a stale duplicate `docs/v0.3.0.md`; release history now lives under
  `docs/releases/`.

## Self-Test

`stui selftest` runs lightweight installed-package checks without launching the
full Textual UI:

```bash
stui selftest
stui selftest --json
```

It validates package metadata, bundled demo resources, all starter templates,
and a copied bundled example through the same non-interactive runtime path as
`stui check`.

`stui selftest` is not a terminal-rendering substitute. Use `stui doctor`,
`stui check`, and a real interactive `stui demo ...` smoke run when debugging
terminal-specific behavior.

## Package Hygiene

v1.3.0 adds a repeatable package audit:

```bash
python scripts/audit_package_contents.py dist
```

The audit verifies that the wheel contains the runtime package, bundled
examples, metadata, entry point, and license; it verifies that the sdist
contains public docs, examples, assets, and maintainer scripts; and it rejects
cache folders, test artifacts, `.DS_Store`, virtual environments, and stale
announcement drafts.

## Screenshot And Demo Alignment

The README/PyPI screenshot remains a real terminal screenshot, not a generated
mock. v1.3.0 makes the pictured app directly runnable from an installed package:

```bash
stui demo model_demo
```

The README image URL is tag-scoped for the v1.3.0 release so PyPI does not
silently drift with future `main` changes.

## API Stability

No top-level `stui` API was removed, renamed, or graduated in v1.3.0.

Still stable:

- v1.0 stable core APIs.
- v1.1 graduated APIs: `st.json`, `st.progress`, `st.table`,
  `st.dataframe`, `st.metric`, `st.number_input`, `st.selectbox`, `st.radio`,
  `st.form`, `st.form_submit_button`, `st.container`, `st.expander`,
  `st.rerun`, and `st.stop`.
- v1.2 stable `st.columns(count)`.

Still experimental:

- `st.bar_chart`
- `st.line_chart`
- `st.status`
- `st.spinner`
- `st.help`

Deferred:

- `st.empty`
- `st.tabs`
- full layout system
- sidebar
- file uploads
- caching
- dataframe editing
- heavier charting
- browser/server runtime

## Upgrade Notes

Existing v1.2.0 apps should continue to work. The changes are additive and
mostly affect CLI validation, release proof, docs organization, and package
artifact hygiene.

## Verification Summary

The release must pass the standard v1 release gates before publication:

- editable install with dev dependencies
- Ruff
- `python3.11 -m pytest`
- build and Twine check
- package contents audit
- `stui --version`
- `python -m stui --version`
- `stui selftest`
- `./scripts/check.sh`
- `scripts/verify_custom_project.sh`
- exhaustive CLI command checks from the repository checkout
- clean wheel install in a temporary virtual environment
- fresh PyPI install after publish
- GitHub CI on `main` and `v1.3.0`
- GitHub Actions Trusted Publishing to PyPI
