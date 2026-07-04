# stui v2.1.0

`stui` v2.1.0 is the first post-v2 feature release. It keeps the full v2.0.0
stable contract intact and adds a small, feedback-oriented batch of
experimental widgets plus a save-and-rerun development loop.

Install it from PyPI:

```bash
python -m pip install --upgrade stui-terminal==2.1.0
```

The package/import/CLI contract remains unchanged:

- PyPI distribution: `stui-terminal`
- Python import: `import stui as st`
- Console command: `stui`

## What Changed

- Added `st.multiselect`, a checkbox-style multi-option selection widget.
  Arrow keys move the highlight, Space or Enter toggles the highlighted
  option, and the widget returns the selected options as a tuple kept in
  options order.
- Added `st.toggle`, an on/off switch with `st.checkbox` semantics.
- Added `st.toast`, a transient terminal notification queued during a script
  run and shown after the run renders.
- Added `stui run APP.py --watch` (short flag `-w`). Watch mode reruns the app
  whenever the script file is saved, keeps `st.session_state` intact across
  reloads, and shows a short `Reloaded ...` notification.
- The app header now shows the running script filename, with `· watching`
  appended in watch mode.
- The bundled `inputs` and `kitchen_sink` examples cover the new widgets.

## Stability

The v2.0.0 stable API is unchanged. `st.status`, `st.spinner`, and `st.help`
remain post-v1 experimental.

The new `st.multiselect`, `st.toggle`, and `st.toast` APIs are classified
`post-v2 experimental`: public enough to use, but outside the v2 stable
contract until real terminal usage confirms their call shapes and keyboard
behavior. Their call shapes may change in a v2.x release with release-note
migration guidance.

`stui run --watch` is additive; `stui run APP.py` behavior is unchanged when
the flag is omitted.

## Feedback

The most useful feedback on the new APIs is specific and tied to a real
terminal workflow: which options list you rendered with `st.multiselect`, how
watch mode behaved with your editor's save behavior, and whether toast
notifications were readable in your terminal and theme.
