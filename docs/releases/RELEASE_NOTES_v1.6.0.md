# stui v1.6.0

`stui` v1.6.0 is a narrow status/help UX and release-safety release. It keeps
the v1.5.0 stable API intact while making the remaining experimental
status/help primitives easier to understand, test, and report on.

Install or upgrade:

```bash
python -m pip install --upgrade stui-terminal==1.6.0
```

## Highlights

- `st.status`, `st.spinner`, and `st.help` remain post-v1 experimental, but
  their current behavior is now documented and tested more directly.
- The kitchen-sink example now exercises `st.status`, `st.spinner`, and
  `st.help`, including visible grouped status content through `expanded=True`.
- `stui doctor --json` and `stui doctor --compat` report unsupported
  `STUI_THEME` values and `NO_COLOR` context more clearly for terminal
  compatibility reports.
- Rich-backed status, spinner, help, alert, and error panels now use
  high-contrast-aware border/text styles.
- The publish workflow now validates that a `v*` Git tag matches
  `pyproject.toml` and `stui.__version__` before building release artifacts.

## API Status

No public APIs were removed or renamed.

Still post-v1 experimental:

- `st.status`
- `st.spinner`
- `st.help`

These stay experimental because `st.status` collapsed-child semantics,
`st.spinner` static grouping behavior, and `st.help` formatting are useful but
not yet frozen as long-term stable contracts.

## Notes

- `st.status(..., expanded=False)` captures child elements when used as a
  context manager, but collapsed status blocks hide those children in the
  visible TUI. Use `expanded=True` when child content should be visible.
- `st.spinner` is a static display/context primitive. It does not animate, run
  background work, or expose a mutable update object.
- `st.help` renders plain text directly or a simple signature/docstring for
  Python objects. It is not a pager or object browser.

## Verification

The release was verified with lint, tests, build, Twine check, package content
audit, exhaustive CLI checks, custom external project validation, CI, PyPI
publish, GitHub Release creation, and a fresh PyPI install smoke test.
