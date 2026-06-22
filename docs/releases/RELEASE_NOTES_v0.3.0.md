# stui v0.3.0

`stui` v0.3.0 is the terminal-app primitives release.

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
It is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Highlights

- Added `st.form` and `st.form_submit_button`.
- Added `st.container` and static `st.expander` grouping primitives.
- Added `st.metric`.
- Added `st.bar_chart` for compact terminal-native bar summaries.
- Added `STUI_THEME=high-contrast`.
- Expanded `stui doctor` with terminal size and resolved theme details.
- Added examples for forms, grouping/layouts, charts, and the expanded kitchen
  sink.

## Examples

```bash
python -m pip install stui-terminal==0.3.0
git clone https://github.com/marmar9615-cloud/stui-terminal.git
cd stui-terminal
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
- No `textual-slider` dependency or copied GPL slider code.
- No heavy plotting dependency.

## Compatibility Notes

Existing 0.2.x APIs remain compatible. The new v0.3.0 primitives are
intentionally small:

- Forms provide a one-shot submit button; widgets inside forms still update
  session state before submit.
- Expanders are static and render open or closed from their initial `expanded`
  argument.
- `st.bar_chart` is a readable terminal summary, not a plotting-library
  replacement.
