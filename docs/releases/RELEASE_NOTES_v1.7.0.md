# stui v1.7.0

`stui` v1.7.0 is an app-authoring and validation release. It keeps the v1.6.0
stable API intact while making installed-user workflows and release validation
stricter, clearer, and easier to run from CI.

Install or upgrade:

```bash
python -m pip install --upgrade stui-terminal==1.7.0
```

## Highlights

- Added `stui check --strict` for authoring validation that fails on warnings
  such as scripts that render no visible elements.
- Added `strict`, `warnings`, and `summary.warning_count` fields to
  `stui check --json`.
- Added `stui selftest --strict` to validate package metadata, bundled demos,
  all bundled examples, all starter templates, and doctor diagnostics without
  launching a full TUI.
- Added `data` and `charts` starter templates:

```bash
stui init data_app.py --template data
stui init charts_app.py --template charts
```

- Improved `stui check` summaries so nested elements inside containers,
  columns, status blocks, expanders, and spinners are counted in validation
  output.
- Tightened release validation scripts and package content audits around
  installed-package examples and external project checks.

## Compatibility

No public Python APIs were removed or renamed. The PyPI distribution remains
`stui-terminal`; the import package and CLI remain `stui`.

`stui` remains terminal-native and Streamlit-inspired, but it is not official
Streamlit, is not affiliated with Streamlit, and is not a Streamlit
compatibility layer. This release does not add browser, server, websocket, or
port-forwarding runtime behavior.

## API Status

No APIs graduated in v1.7.0.

Still post-v1 experimental:

- `st.status`
- `st.spinner`
- `st.help`

## Validation Notes

`stui check --strict` still executes user app code through the normal `stui`
runtime. It is an authoring and CI validation aid, not a sandbox, static linter,
or visual terminal renderer.

Warning-only strict failures return JSON with `status: "ok"`, `error: null`,
`strict: true`, and a non-empty `warnings` list. Script errors, syntax errors,
duplicate-key errors, and invalid script paths keep their existing error
behavior.

## Verification

The release was verified with lint, tests, build, Twine check, package content
audit, exhaustive CLI checks, strict selftest/check flows, custom external
project validation, CI, PyPI publish, GitHub Release creation, and a fresh PyPI
install smoke test.
