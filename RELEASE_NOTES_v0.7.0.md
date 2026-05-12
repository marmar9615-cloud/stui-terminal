# stui v0.7.0

`stui` v0.7.0 is the API contract readiness release.

This is not the v1 launch and not a Streamlit compatibility promise. Public
launch-style announcement pushes are saved for v1.0.0, after the stable API,
PyPI install path, examples, docs, CI, and terminal compatibility checks are
verified together.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- README now links directly to the API contract status, stable API candidate,
  API reference, and terminal compatibility checklist.
- Added pre-v1 experimental `st.status(...)`, `st.spinner(...)`, and
  `st.help(...)` as small terminal-native status/help primitives while their v1
  contract gathers feedback.
- Layout primitives are labeled more precisely: `st.container`, `st.columns`,
  and `st.expander` are terminal grouping helpers. Columns remain pre-v1
  experimental and are not a sidebar, tabs, grid, or full layout engine.
- Installed-package examples are easier to discover and copy with
  `stui examples`, `stui example list`, `stui example copy ...`, and
  `stui init ...`.
- Limitations and non-goals now call out the project boundaries explicitly:
  no browser runtime, no server/websocket/port-forwarding flow, no Streamlit
  runtime dependency, no Streamlit compatibility layer, no hosted/cloud product
  scope, and no GPL slider/widget dependency path.
- `docs/v1-readiness.md` now tracks API contract status,
  stable/experimental status, remaining blockers, and the v0.8/v0.9 path.
- `ROADMAP.md` and `docs/feedback.md` now emphasize terminal evidence,
  package-hardening checks, API contract mismatch reports, and layout feedback.

## API Contract Status

The public contract is documented in `docs/api-reference.md`. v0.7.0 treats
that document as the current contract, but not a v1 freeze. Public signature,
return-value, or semantic changes before v1 should be called out in the
changelog and release notes.

Stable-candidate areas:

- Text and basic status output.
- Static display helpers, including table/dataframe output with static-display
  limits.
- Input widgets with keys, disabled state, callbacks, and documented return
  values.
- Forms and submit buttons with deferred `session_state` commit on submit.
- `st.container` and `st.expander` as terminal grouping primitives.
- `st.session_state`, `st.rerun`, and `st.stop`.
- CLI commands for app runs, diagnostics, examples, starter generation, and
  version output.

Experimental or intentionally modest areas:

- `st.status`, `st.spinner`, and `st.help` are public but pre-v1 experimental
  while their terminal grouping/help formatting contract is refined.
- `st.metric`, `st.bar_chart`, and `st.line_chart` are compact terminal
  summaries, not plotting-library replacements.
- `st.columns` is a simple responsive terminal primitive. It accepts only an
  integer count and stacks on narrow terminals.
- Tables/dataframes are static displays without editing, sorting, selection,
  pagination, pandas-specific integrations, or formatting hooks.
- Layout remains terminal-first. Sidebars, tabs, grids, custom ratios,
  horizontal scrolling, and larger layout engines are not part of the v0.7.0
  contract.
- Terminal compatibility claims remain evidence-driven and should not be
  broadened without checks in real environments.

## Verification

Before publishing v0.7.0, run:

```bash
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
```

Also verify representative installed-package flows:

```bash
stui examples
stui example list
stui example copy counter ./counter.py
stui example copy forms ./forms_app.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
python -m stui run ./counter.py
python -m stui run ./forms_app.py
python -m stui run ./new_app.py
python -m stui run ./dashboard.py
```

## Boundaries

- No browser runtime.
- No local web server, websocket, or port-forwarding flow.
- No Streamlit runtime dependency.
- No claim of Streamlit compatibility.
- No copied GPL slider code or `textual-slider` dependency.
- No X, LinkedIn, or other social launch copy for this pre-1.0 release.
- Public announcement push remains saved for v1.0.0.
