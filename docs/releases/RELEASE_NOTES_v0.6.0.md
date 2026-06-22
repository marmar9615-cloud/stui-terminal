# stui v0.6.0

`stui` v0.6.0 is the compatibility and API-stability readiness release.

This is not the v1 launch. Public launch-style announcement pushes are saved for
v1.0.0, after the stable API, PyPI install path, examples, docs, CI, and
terminal compatibility checks are verified together.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- README now links to the API reference, v1 API stability checklist, and
  terminal compatibility checklist.
- The API table now labels the v0.6.0 public surface as stable-candidate or
  experimental instead of implying broad Streamlit compatibility.
- Install docs now emphasize the `stui-terminal` PyPI distribution, the `stui`
  import package, the `stui` CLI, and the `python -m stui` fallback.
- Example docs now cover repository examples, bundled example listing/copying,
  and `stui init` templates.
- `docs/v1-readiness.md` now tracks API stability status, known limitations,
  terminal compatibility status, and remaining v1 gates.
- `ROADMAP.md` now separates the v0.6 compatibility pass, v0.7 API reference
  and release-candidate prep, v0.8 terminal evidence and hardening, and v1.
- `docs/feedback.md` now asks directly for terminal reports, keyboard bugs,
  narrow-rendering bugs, API signature confusion, docs gaps, and example gaps.

## Compatibility Notes

The v0.6.0 line is still pre-1.0. It does not claim a v1 API freeze and does
not add Streamlit compatibility.

Stable-candidate APIs should be treated as the working v1 surface, but final
signature and return-value docs still need to be completed before v1.

Experimental or intentionally modest areas remain:

- `st.metric`, `st.bar_chart`, and `st.line_chart` are compact terminal
  summaries, not plotting-library replacements.
- `st.table` and `st.dataframe` are static display helpers without editing or
  sorting.
- `st.container` and `st.expander` are grouping primitives, not a full layout
  engine.
- Forms keep pending values out of `session_state` until submit, while the
  Textual app may still rerun during widget edits.

The package should continue to install from PyPI as `stui-terminal`, while the
import package and CLI remain `stui`.

## Verification

Before publishing v0.6.0, run:

```bash
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
```

Also verify representative examples with `stui run` or `python -m stui run`,
including:

```bash
stui run examples/basic.py
stui run examples/counter.py
stui run examples/forms.py
stui run examples/layouts.py
stui run examples/charts.py
stui run examples/kitchen_sink.py
stui example list
stui example copy counter ./counter.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
```

## Boundaries

- No browser runtime.
- No local web server, websocket, or port-forwarding flow.
- No Streamlit runtime dependency.
- No claim of Streamlit compatibility.
- No copied GPL slider code or `textual-slider` dependency.
- No X or LinkedIn launch copy for this pre-1.0 release.
- Public announcement push remains saved for v1.0.0.
