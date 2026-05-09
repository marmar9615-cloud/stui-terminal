# stui v0.2.0rc1

`stui` v0.2.0rc1 expands the tiny terminal-native Streamlit-inspired API into a
more useful release candidate while keeping the same clean-room, no-browser
runtime.

## Install

```bash
python -m pip install stui-terminal==0.2.0rc1
```

The PyPI distribution is `stui-terminal`; the import package and CLI remain
`stui`.

## Highlights

- Added display APIs:
  - `st.subheader`
  - `st.caption`
  - `st.code`
  - `st.json`
  - `st.exception`
  - `st.progress`
- Added input APIs:
  - `st.number_input`
  - `st.selectbox`
  - `st.radio`
- Added data display:
  - `st.table`
  - `st.dataframe` as a table alias
- Added CLI helpers:
  - `stui doctor`
  - `stui examples`
- Added examples:
  - `examples/inputs.py`
  - `examples/data_display.py`
  - `examples/dashboard.py`

## Still Intentionally Missing

- No charts yet.
- No full dataframe interaction.
- No columns, sidebar, forms, caching, or file upload.
- No browser, web server, websocket, or port-forwarding runtime.
- No Streamlit dependency and no claim of full Streamlit compatibility.

## Verification

This release candidate should be published only after local tests, lint, build,
twine checks, GitHub CI, and static safety checks pass.
