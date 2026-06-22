# API Stability

`stui` v1.6.0 keeps the top-level stable API intentionally small and
Streamlit-inspired, but it is not Streamlit-compatible and does not depend on
Streamlit at runtime.

This page classifies the names exported by:

```python
import stui as st
```

Anything outside the top-level `stui.__all__` surface is private unless a future
release explicitly documents it here and in `docs/api-reference.md`.

## v1 Compatibility Contract

`v1-stable` means the API is part of the stable v1 contract. The project intends
to keep the name, call shape, return type, and basic behavior compatible through
the v1 series unless a correctness bug, terminal limitation, or security issue
makes a change necessary.

`post-v1 experimental` means the API is public enough to use, but still needs
feedback before it can graduate into the stable contract. It may change in a
v1.x release. Changes should be called out in release notes with a migration
path when practical.

`internal/private` means the API is not supported for user code. It may move,
rename, or disappear without deprecation, even when it is importable for tests or
implementation reasons.

`deferred for v1` means a familiar Streamlit-style name or feature area is
intentionally not part of the v1 stable API. It should not be added casually
without updating this page, the API reference, the README API table, the v1
readiness checklist, and public API tests.

There are no current top-level `stui.__all__` exports marked for removal or
rename in the v1.x line.

## Top-Level API Classification

<!-- API_CLASSIFICATION_START -->
| API | Classification | Notes |
| --- | --- | --- |
| `__version__` | v1-stable | Package version string. |
| `bar_chart` | v1-stable | Compact terminal bar summary, not plotting-library parity. |
| `button` | v1-stable | Core input widget. |
| `caption` | v1-stable | Core text output. |
| `checkbox` | v1-stable | Core input widget. |
| `code` | v1-stable | Core text output. |
| `columns` | v1-stable | Count-only responsive terminal columns that stack on narrow terminals and inside narrow parent columns. |
| `container` | v1-stable | Terminal grouping primitive, not a full layout engine. |
| `dataframe` | v1-stable | Static terminal display; editing and sorting are out of scope. |
| `divider` | v1-stable | Core visual separator. |
| `error` | v1-stable | Core status output. |
| `exception` | v1-stable | Core status output for exceptions. |
| `expander` | v1-stable | Keyboard-toggleable terminal grouping primitive. |
| `form` | v1-stable | Deferred submit behavior is part of the v1 contract. |
| `form_submit_button` | v1-stable | One-shot form submit button. |
| `header` | v1-stable | Core text output. |
| `help` | post-v1 experimental | Help formatting and the public name need more feedback. |
| `info` | v1-stable | Core status output. |
| `json` | v1-stable | Static terminal JSON display with string fallback. |
| `line_chart` | v1-stable | Compact terminal sparkline summary, not plotting-library parity. |
| `markdown` | v1-stable | Core text output. |
| `metric` | v1-stable | Compact terminal summary display. |
| `number_input` | v1-stable | Numeric input widget. |
| `progress` | v1-stable | Clamped terminal progress display. |
| `radio` | v1-stable | Selection input widget. |
| `rerun` | v1-stable | Flow-control helper for explicit reruns. |
| `selectbox` | v1-stable | Selection input widget. |
| `session_state` | v1-stable | Core state mapping and attribute proxy. |
| `slider` | v1-stable | Core numeric input widget. |
| `spinner` | post-v1 experimental | Status grouping behavior may still tighten in v1.x. |
| `stop` | v1-stable | Flow-control helper that halts the current script pass. |
| `subheader` | v1-stable | Core text output. |
| `status` | post-v1 experimental | Status grouping behavior may still tighten in v1.x. |
| `success` | v1-stable | Core status output. |
| `table` | v1-stable | Static terminal table display. |
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
surface:

<!-- API_DEFERRED_START -->
| API or area | v1 status | Notes |
| --- | --- | --- |
| `st.sidebar` | deferred for v1 | No sidebar layout primitive in the terminal-first v1 surface. |
| `st.tabs` | deferred for v1 | No tabbed layout primitive in the v1 surface. |
| `st.file_uploader` | deferred for v1 | File upload is out of scope for the local terminal MVP. |
| `st.cache_data` | deferred for v1 | Caching decorators are out of scope for the v1 API freeze. |
| `st.cache_resource` | deferred for v1 | Caching decorators are out of scope for the v1 API freeze. |
| `st.components` | deferred for v1 | Browser component embedding is intentionally unsupported. |
| `st.empty` | deferred for v1 | Placeholder mutation semantics are not frozen for the terminal rerun model. |
| custom column ratios/gaps | deferred for v1 | `st.columns` remains a count-only terminal primitive. |
| editable dataframes | deferred for v1 | `st.dataframe` remains static display only. |
| plotting-library parity | deferred for v1 | Charts remain compact terminal summaries. |
| browser/server runtime | deferred for v1 | No browser, server, websocket, or port-forwarding runtime is planned for v1. |
<!-- API_DEFERRED_END -->

## Post-v1 Deprecations

The top-level `v1-stable` APIs are the compatibility contract for the v1 series.
Stable public APIs should not be removed or renamed in a v1.x release. A normal
deprecation should:

- document the replacement in `docs/api-reference.md` and release notes;
- keep the old name working through the rest of the v1 series when practical;
- warn clearly before removal when warnings are technically reasonable;
- remove the deprecated API only in the next major release, unless keeping it
  would create a security, data-loss, or severe correctness problem.

Changing the call shape, return type, or basic behavior of a stable API during
the v1 series should be treated like a removal: avoid it unless the existing
behavior is incorrect, unsafe, or impossible to support in terminals. When such
a change is unavoidable, document the reason, migration path, and affected
versions in the changelog, release notes, API reference, and public API tests.

Post-v1 experimental APIs must keep that label in the API reference. They may
change in a v1.x minor release, but the release notes should explain the
migration path when practical. Promoting an experimental API to stable requires
updating this page, the API reference, the README API table, the v1 readiness
docs, and `tests/test_public_api.py` in the same release.
