# API Stability

`stui` is still before v1.0.0. The top-level API is intentionally small and
Streamlit-inspired, but it is not Streamlit-compatible and does not depend on
Streamlit at runtime.

This page classifies the names exported by:

```python
import stui as st
```

Anything outside the top-level `stui.__all__` surface is private unless a future
release explicitly documents it here and in `docs/api-reference.md`.

## Compatibility Before v1.0.0

v0.9.0 is the final pre-v1 candidate line. The project should treat the
`v1-stable` rows below as frozen for v1.0.0 unless a correctness bug, terminal
limitation, or security issue makes a change necessary. Any such change needs a
changelog entry, release-note coverage, and synchronized README/API reference
updates.

`v1-stable` means the API is a stable candidate for v1. The project intends to
keep the name, call shape, return type, and basic behavior compatible through
the remaining 0.x releases unless a correctness bug, terminal limitation, or
security issue makes a change necessary.

`pre-v1 experimental` means the API is public enough to use, but still needs
feedback before v1. It may change in a 0.x release. Changes should be called out
in release notes with a migration path when practical.

`internal/private` means the API is not supported for user code. It may move,
rename, or disappear without deprecation, even when it is importable for tests or
implementation reasons.

`deferred for v1` means a familiar Streamlit-style name or feature area is
intentionally not part of the v1 candidate API. It should not be added casually
without updating this page, the API reference, the README API table, the v1
readiness checklist, and public API tests.

`candidate for removal/rename before v1` means a public name is known to need a
decision before v1.0.0. There are no current top-level `stui.__all__` exports in
that category.

## Top-Level API Classification

<!-- API_CLASSIFICATION_START -->
| API | Classification | Notes |
| --- | --- | --- |
| `__version__` | v1-stable | Package version string. |
| `bar_chart` | pre-v1 experimental | Terminal chart rendering may still tighten before v1. |
| `button` | v1-stable | Core input widget. |
| `caption` | v1-stable | Core text output. |
| `checkbox` | v1-stable | Core input widget. |
| `code` | v1-stable | Core text output. |
| `columns` | pre-v1 experimental | Responsive terminal layout behavior may still tighten. |
| `container` | pre-v1 experimental | Terminal grouping primitive, not a full layout engine. |
| `dataframe` | pre-v1 experimental | Static terminal display; editing and sorting are out of scope. |
| `divider` | v1-stable | Core visual separator. |
| `error` | v1-stable | Core status output. |
| `exception` | v1-stable | Core status output for exceptions. |
| `expander` | pre-v1 experimental | Terminal grouping behavior may still tighten. |
| `form` | pre-v1 experimental | Deferred submit behavior and callback timing need v1 feedback. |
| `form_submit_button` | pre-v1 experimental | Coupled to experimental form semantics. |
| `header` | v1-stable | Core text output. |
| `help` | pre-v1 experimental | Help formatting and the public name need v1 feedback. |
| `info` | v1-stable | Core status output. |
| `json` | pre-v1 experimental | Static terminal display formatting may change. |
| `line_chart` | pre-v1 experimental | Terminal chart rendering may still tighten before v1. |
| `markdown` | v1-stable | Core text output. |
| `metric` | pre-v1 experimental | Compact terminal summary formatting may change. |
| `number_input` | pre-v1 experimental | Newer input widget still gathering feedback. |
| `progress` | pre-v1 experimental | Terminal rendering and normalization may still tighten. |
| `radio` | pre-v1 experimental | Newer selection widget still gathering feedback. |
| `rerun` | pre-v1 experimental | Flow-control semantics need real-app feedback. |
| `selectbox` | pre-v1 experimental | Newer selection widget still gathering feedback. |
| `session_state` | v1-stable | Core state mapping and attribute proxy. |
| `slider` | v1-stable | Core numeric input widget. |
| `spinner` | pre-v1 experimental | Status grouping behavior may still tighten before v1. |
| `stop` | pre-v1 experimental | Flow-control semantics need real-app feedback. |
| `subheader` | v1-stable | Core text output. |
| `status` | pre-v1 experimental | Status grouping behavior may still tighten before v1. |
| `success` | v1-stable | Core status output. |
| `table` | pre-v1 experimental | Static terminal display formatting may change. |
| `text` | v1-stable | Core text output. |
| `text_input` | v1-stable | Core input widget. |
| `title` | v1-stable | Core text output. |
| `warning` | v1-stable | Core status output. |
| `write` | v1-stable | Core text/value output. |
<!-- API_CLASSIFICATION_END -->

## Internal and Private APIs

These import paths are implementation details and are not part of the public
contract:

- `stui.api.SessionStateProxy`
- `stui.app.*`, including Textual widget subclasses and theme helpers
- `stui.cli.*`, except the installed `stui` command itself
- `stui.elements.*` dataclasses
- `stui.runtime.*`, including runtime classes and control-flow exceptions
- `stui.session_state.SessionState`
- `stui.widgets.*`, including `StuiSlider` and `snap_value`

Tests may import these names to verify behavior, but user code should rely on
the top-level `stui` API documented above.

## Deferred For v1

These APIs and feature areas are explicitly deferred from the v1 stable
candidate surface:

<!-- API_DEFERRED_START -->
| API or area | v1 status | Notes |
| --- | --- | --- |
| `st.sidebar` | deferred for v1 | No sidebar layout primitive in the terminal-first v1 surface. |
| `st.tabs` | deferred for v1 | No tabbed layout primitive in the v1 surface. |
| `st.file_uploader` | deferred for v1 | File upload is out of scope for the local terminal MVP. |
| `st.cache_data` | deferred for v1 | Caching decorators are out of scope for the v1 API freeze. |
| `st.cache_resource` | deferred for v1 | Caching decorators are out of scope for the v1 API freeze. |
| `st.components` | deferred for v1 | Browser component embedding is intentionally unsupported. |
| custom column ratios/gaps | deferred for v1 | `st.columns` remains a count-only experimental terminal primitive. |
| editable dataframes | deferred for v1 | `st.dataframe` remains static display only. |
| plotting-library parity | deferred for v1 | Charts remain compact terminal summaries. |
| browser/server runtime | deferred for v1 | No browser, server, websocket, or port-forwarding runtime is planned for v1. |
<!-- API_DEFERRED_END -->

## Post-v1 Deprecations

After v1.0.0, stable public APIs should not be removed or renamed in a v1.x
release without a deprecation period. A normal deprecation should:

- document the replacement in `docs/api-reference.md` and release notes;
- keep the old name working for at least one minor release when practical;
- warn clearly before removal when warnings are technically reasonable;
- remove the deprecated API only in the next major release, unless keeping it
  would create a security, data-loss, or severe correctness problem.

Experimental APIs that remain experimental after v1 must keep that label in the
API reference and explain their narrower compatibility promise.
