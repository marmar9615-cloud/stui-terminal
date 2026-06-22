# stui v1.8.0

`stui` v1.8.0 is a performance, reliability, and long-run quality release. It
keeps the v1.7.0 public API intact while tightening release evidence around
reruns, installed-package validation, package audits, and recovery from
authoring/runtime edge cases.

## Install

```bash
python -m pip install --upgrade stui-terminal==1.8.0
```

The PyPI distribution remains `stui-terminal`; the import package and CLI remain
`stui`.

## Highlights

- Added `stui check --repeat N` for repeated non-interactive validation in one
  runtime.
- Added `stui selftest --repeat N` for repeated installed-package template and
  bundled-example checks.
- Added per-run JSON summaries to `stui check --json`.
- Tightened package contents audit checks for expected versions, entry points,
  metadata, and archive path safety.
- Added `scripts/benchmark_runtime.py` as an advisory maintainer timing probe
  with no CI timing threshold.
- Kept the v1 stable API unchanged.

## Reliability Fixes

- Duplicate-key and API-usage errors no longer commit pending widget changes
  from a failed authoring run.
- Form submits now discard pending values for form widgets that are hidden in
  the submit run.
- Consecutive rerun exhaustion restores the session state from before the
  runaway run.

## Compatibility

No public Python APIs were removed or renamed. `st.status`, `st.spinner`, and
`st.help` remain post-v1 experimental.

## Verification

The release was verified with local lint, tests, build, `twine check`, package
contents audit, repeated strict selftest/check flows, custom external project
validation, GitHub CI on `main` and tag, real PyPI publish, GitHub Release
creation, and a fresh exact-version PyPI install.
