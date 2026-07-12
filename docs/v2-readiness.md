# v2 Readiness

`stui` v2.0.0 established the stable v2 contract. v2.3.0 is the interactive
workspaces and deep diagnostics release: it preserves compatibility while
adding experimental tabs, local path input, selectable data, and versioned
non-sensitive inspection.

`stui` remains terminal-native, Streamlit-inspired, and deliberately not
Streamlit-compatible. The PyPI distribution remains `stui-terminal`; the import
package and CLI remain `stui`.

## v2.0.0 Release Decision

v2.0.0 ships when all of these are true:

- the stable API list below matches `docs/api-stability.md`,
  `docs/api-reference.md`, the README API table, and `tests/test_public_api.py`;
- experimental APIs are still clearly labeled or explicitly promoted with tests
  and migration notes;
- deferred APIs remain documented as post-v2 work;
- local lint, tests, build, `twine check`, release-version checks, package
  contents audit, and static policy checks pass;
- fresh wheel install, fresh PyPI install, exhaustive CLI checks, and custom
  external project validation pass;
- GitHub CI passes on `main` and the tag;
- PyPI publish and GitHub Release proof are verified before saying v2 shipped.

## Stable API

These APIs are the v2.0.0 stable contract. They should keep their top-level
names, signatures, return values, and basic behavior unless a correctness,
terminal, or security issue requires tightening.

| Area | APIs |
| --- | --- |
| Text | `st.title`, `st.header`, `st.subheader`, `st.caption`, `st.text`, `st.markdown`, `st.write`, `st.divider`, `st.code` |
| Status | `st.info`, `st.success`, `st.warning`, `st.error`, `st.exception` |
| Display | `st.json`, `st.progress`, `st.table`, `st.dataframe`, `st.metric`, `st.bar_chart`, `st.line_chart` |
| Inputs | `st.button`, `st.slider`, `st.text_input`, `st.text_area`, `st.checkbox`, `st.toggle`, `st.number_input`, `st.selectbox`, `st.radio` |
| Forms and grouping | `st.form`, `st.form_submit_button`, `st.container`, `st.expander`, `st.columns` |
| Caching | `st.cache_data`, `st.cache_resource` |
| State and flow | `st.session_state`, `st.rerun`, `st.stop` |
| Package metadata | `st.__version__` |
| CLI | `stui run`, `stui check`, `stui demo list`, `stui demo NAME`, `stui examples`, `stui example list`, `stui example copy`, `stui init`, `stui doctor`, `stui selftest`, `stui --version` |

## Experimental APIs

These APIs remain public but experimental in v2.3.0:

- `st.status`
- `st.spinner`
- `st.help`
- `st.multiselect`
- `st.toast`
- `st.tabs`
- `st.path_input`
- `st.data_table`

They are tested and documented, but their exact terminal formatting, keyboard,
serialization/invalidation, notification lifecycle, or grouping behavior still
needs more real use before being called stable.

## Deferred Roadmap

These APIs and feature areas are explicitly deferred from the v2.0.0 stable
contract:

- `st.sidebar`
- `st.file_uploader`
- `st.components`
- `st.empty`
- custom column ratios/gaps
- editable dataframes
- plotting-library parity
- browser/server runtime

## Migration Notes From v1.x

No migration is required for apps that use the v1.9.0 stable candidate API.
The v2.0.0 release preserves the `stui-terminal` distribution name,
`stui` import package, `stui` console command, and documented CLI workflow.

Apps using `st.status`, `st.spinner`, or `st.help` should treat those APIs as
experimental until they are promoted in release notes.

The v2.3 release graduates the process-local cache decorators, multiline text
area, and toggle. Cache APIs still do not promise Streamlit compatibility;
`st.text_area` uses Ctrl+Enter to apply and Enter to insert a newline.

## v2.3.0 Release Decision

v2.3.0 is ready only when evidence proves all of the following:

- tab state, nested panes, hidden focus, forms, callbacks, and palette switching
  behave predictably;
- path input validates metadata without reading file contents or claiming a
  sandbox boundary;
- interactive tables preserve source-row indexes across truncation and handle
  empty, uneven, Unicode, narrow, keyboard, and mouse cases;
- `stui check` and `stui inspect` traverse all tab panes while JSON inspection
  suppresses user stdout/stderr and never exposes runtime values;
- macOS and Windows clean-wheel jobs exercise imports, workspace templates,
  inspect, strict check, selftest, demos, and examples;
- local gates, custom external-project proof, package audit, security/static
  review, main/tag CI, Trusted Publishing, PyPI, GitHub Release, and a fresh
  exact-version install all pass.

## v2.2.0 Release Decision

v2.2.0 is ready only when evidence proves all of the following:

- cache keys are app-scoped, argument-normalized, code-sensitive, and isolated
  between unrelated scripts;
- `st.cache_data` protects cached values from mutation, while
  `st.cache_resource` preserves object identity;
- TTL, LRU entry limits, per-function clearing, namespace clearing,
  unsupported-value errors, and no-exception-caching behavior are covered by
  deterministic tests;
- watch mode detects imported local-module changes, evicts stale modules,
  preserves `st.session_state`, invalidates changed decorated functions, and
  recovers after temporary syntax/import/runtime errors;
- `st.text_area` covers multiline input, Ctrl+Enter apply, callbacks, forms,
  disabled state, length limits, Unicode, and narrow-terminal rendering;
- the repo examples and bundled copies are synchronized;
- a clean wheel install and an external multi-file project prove the cache,
  watch, input, CLI, and package-resource behavior outside the checkout;
- local gates, security/static policy, main/tag CI, Trusted Publishing, PyPI,
  GitHub Release, and fresh exact-version PyPI install all pass.

`st.tabs` is not part of v2.2.0. The current top-to-bottom element model does
not yet have a sufficiently small, tested answer for inactive-content
execution, state/key behavior, nested forms/containers, focus restoration, and
narrow-terminal navigation.

## Final v2 Checklist

Before publishing v2.0.0:

- bump versions in `pyproject.toml` and `src/stui/__init__.py`;
- update README, `docs/api-reference.md`, `docs/api-stability.md`,
  `docs/v2-readiness.md`, `ROADMAP.md`, `CHANGELOG.md`, and
  `docs/releases/RELEASE_NOTES_v2.0.0.md`;
- run the full local verification gate from `docs/release-checklist.md`;
- run exhaustive CLI checks from both the repo checkout and a clean wheel
  install;
- run custom external project validation with the built wheel;
- verify the previous public PyPI version before publishing;
- wait for GitHub CI on `main` and the tag;
- publish with Trusted Publishing only after all gates pass;
- verify fresh exact-version PyPI install;
- create the GitHub Release from `docs/releases/RELEASE_NOTES_v2.0.0.md`;
- confirm the working tree is clean.
