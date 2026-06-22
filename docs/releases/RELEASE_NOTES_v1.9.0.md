# stui v1.9.0

`stui` v1.9.0 is the final v2.0.0 candidate. It does not add a broad feature
batch. Instead, it freezes the v2 candidate API contract, clarifies the
remaining experimental APIs, fixes two final form-state edge cases, and makes
the v2 release checklist explicit.

## Install

```bash
python -m pip install --upgrade stui-terminal==1.9.0
```

The PyPI distribution remains `stui-terminal`; the import package and CLI remain
`stui`.

## Highlights

- Added `docs/v2-readiness.md` as the v2.0.0 checklist and migration contract.
- Added tests that verify the v2 readiness stable and experimental API lists
  match the canonical API stability table.
- Kept the stable public API unchanged from v1.8.0.
- Kept `st.status`, `st.spinner`, and `st.help` experimental for the v2
  candidate unless v2.0.0 explicitly promotes them.
- Updated README, API docs, release checklist, roadmap, feedback docs, and
  v1-readiness docs for the v2 candidate state.

## Fixes

- Disabled form widgets now discard stale pending values from earlier enabled
  runs instead of committing them on a later submit.
- Empty `st.selectbox` and `st.radio` widgets inside forms no longer mutate
  `st.session_state` before submit.

## Compatibility

No public Python APIs were removed or renamed. Existing v1.8.0 apps should keep
working without code changes.

## v2.0.0 Candidate Status

v2.0.0 should be a contract and release-proof milestone, not a risky feature
wave. The final v2 release should verify:

- local lint, tests, build, `twine check`, package audit, and release-version
  checks;
- clean wheel install and fresh PyPI install;
- exhaustive CLI checks, repeated `stui check`, repeated `stui selftest`, and
  custom external project validation;
- GitHub CI on `main` and tag;
- PyPI publish and GitHub Release proof;
- clean repo/package hygiene.

## Experimental APIs

Still post-v1 experimental:

- `st.status`
- `st.spinner`
- `st.help`

These APIs are public enough to try, but their exact formatting/grouping/help
contract remains open to feedback.

## Verification

The release was verified with local lint, tests, build, `twine check`, package
contents audit, repeated strict selftest/check flows, custom external project
validation, GitHub CI on `main` and tag, real PyPI publish, GitHub Release
creation, and a fresh exact-version PyPI install.
