# stui v0.5.0

`stui` v0.5.0 is the developer-experience, runner robustness, keyboard polish,
and documentation readiness release.

This is not the v1 launch. Public launch-style announcement pushes are saved for
v1.0.0, after the stable API, PyPI install path, examples, docs, CI, and
terminal compatibility checks are verified together.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- README now has clearer install instructions for `stui-terminal`, the `stui`
  import package, and the `stui` CLI.
- The 60-second quickstart and first-app walkthrough now show the intended
  top-to-bottom rerun model with `st.session_state`.
- CLI docs now cover `stui run`, `python -m stui run`, `stui examples`,
  `stui example list`, `stui example copy`, `stui init`, `stui doctor`, and
  `stui --version`.
- `st.stop()` now halts the current script pass without a traceback while
  preserving already-rendered elements and `session_state`.
- Runtime errors for missing files, syntax errors, and import errors now render
  with less `runpy` noise.
- Script execution now restores `sys.path` after each run, even if the user
  script mutates it.
- `stui examples` now includes descriptions, bundled/repo source labels, and
  exact copy/run commands.
- `stui init` now supports `--template basic`, `--template dashboard`, and
  `--template forms`.
- `stui doctor` now reports terminal size, `TERM`, `COLORTERM`, stdin/stdout/
  stderr TTY status, color capability, theme, dependency versions, and
  small-terminal warnings.
- Keyboard polish improves focused-control help and arrow behavior for
  selectbox, radio, expander, and slider controls.
- The API table now describes the v0.5.0 stability candidate surface instead of
  implying Streamlit compatibility.
- Keyboard docs now cover focus movement, buttons, text and number inputs,
  checkboxes, selectboxes, radio groups, sliders, expanders, quit, and rerun.
- Terminal compatibility guidance now points to `docs/terminal-compatibility.md`
  and `docs/v1-readiness.md`.
- Feedback docs now request terminal reports, keyboard issues, install/package
  issues, API confusion, and desired examples.
- The roadmap now describes the v0.5, v0.6, v0.7, and v1 path.

## Compatibility Notes

The v0.5.0 line is still pre-1.0. It does not claim a v1 API freeze and does
not add Streamlit compatibility.

The package should continue to install from PyPI as `stui-terminal`, while the
import package and CLI remain `stui`.

## Verification

Before publishing v0.5.0, run:

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
```

## Boundaries

- No browser runtime.
- No local web server, websocket, or port-forwarding flow.
- No Streamlit runtime dependency.
- No claim of Streamlit compatibility.
- No copied GPL slider code or `textual-slider` dependency.
- No X or LinkedIn launch copy for this pre-1.0 release.
- Public announcement push remains saved for v1.0.0.
