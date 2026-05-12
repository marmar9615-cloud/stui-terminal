# stui v0.4.0

`stui` v0.4.0 is the correctness and interactions release.

This is not the v1 launch. Public launch-style announcements should wait for
v1.0.0, after the stable API, PyPI install path, examples, docs, and terminal
compatibility checks are verified.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- Form widget values are now deferred from `session_state` until
  `st.form_submit_button` commits the form.
- Form callbacks run after commit and before the submitted branch continues.
- `st.expander` is now keyboard-toggleable with Enter/Space and persists state
  under an explicit or generated key.
- `st.bar_chart` handles signed, zero-only, non-finite, and narrow-width data
  more defensively.
- `st.line_chart` adds a compact terminal sparkline helper for numeric lists and
  dictionaries of numeric series.
- Bundled example apps can be listed with `stui examples` and copied with
  `stui example copy`.
- `stui init APP.py` creates a small starter app.
- `docs/v1-readiness.md` now records the path to a credible v1.0.0.

## Compatibility Notes

The v0.4.0 line preserves the v0.3.0 API surface while tightening form state
semantics before v1.0.0.

The package should continue to install from PyPI as `stui-terminal`, while the
import package and CLI remain `stui`.

## Verification

Before publishing v0.4.0, run:

```bash
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
```

Also verify representative examples with `stui run` or `python -m stui run`,
including:

```bash
stui run examples/forms.py
stui run examples/layouts.py
stui run examples/charts.py
stui run examples/kitchen_sink.py
```

## Boundaries

- No browser runtime.
- No local web server, websocket, or port-forwarding flow.
- No Streamlit runtime dependency.
- No claim of Streamlit compatibility.
- No copied GPL slider code or `textual-slider` dependency.
- No public launch posts for this pre-1.0 release.
