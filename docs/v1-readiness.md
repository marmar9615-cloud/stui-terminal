# v1 Readiness

`stui` v1.0.0 is the first stable release. The goal for v1 is not to become
Streamlit-compatible or to grow a large component catalog. The goal is a small,
stable, terminal-native API that can be installed from PyPI, explained quickly,
and trusted for local tools.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Status After v1.0.0

v1.0.0 turns the final pre-v1 candidate into a stable baseline. It freezes the
stable API list, keeps experimental APIs labeled, aligns install/demo/init/example
docs with installed-package behavior, and moves unresolved larger features into
post-v1 roadmap buckets instead of hiding them.

On the v1.0.0 line, the stable API list is frozen. The freeze covers the
top-level names in `stui.__all__`, their stability classifications, and the
documented function signatures. Bug fixes may still tighten behavior, but
adding, removing, renaming, or changing a stable top-level public API requires
synchronized updates to `README.md`,
`docs/api-reference.md`, `docs/api-stability.md`, this page, release notes, and
`tests/test_public_api.py`.

Terminal compatibility evidence remains intentionally evidence-driven. Unknown
or untested environments stay labeled test-needed, while supported flows are
verified through CI, fresh PyPI installs, bundled examples, and local smoke
checks.

Public launch copy is prepared for v1.0.0, but social posts should still be
posted manually only after the exact PyPI package, GitHub Release, and fresh
install checks are verified.

## Complete For v1.0.0

- The PyPI distribution/import/CLI naming is settled: install
  `stui-terminal`, import `stui`, and run `stui`.
- The stable API is documented in the README, API reference, API
  stability table, and public API tests.
- Experimental APIs remain labeled instead of being quietly promoted for launch.
- Deferred Streamlit-style features are listed as out of scope for v1.
- The README quickstart, first app, API table, terminal compatibility link,
  examples/templates, limitations, and troubleshooting sections all point users
  at the same v1.0.0 contract.
- Bundled demo/example listing/copying and `stui init` are part of the v1
  documentation contract rather than checkout-only conveniences.
- Public launch copy is drafted for manual posting after release verification.

## Post-v1 Verification Habits

- Re-run the full release checklist against exact release artifacts for every
  patch/minor release, not only the editable checkout.
- Verify PyPI install from a clean virtual environment after publish.
- Keep the terminal compatibility matrix evidence-driven and leave unsupported
  environments labeled unknown or test-needed.
- Confirm PyPI/GitHub screenshots and docs still represent real shipped apps.

## API Stability Status

The project should keep the public API small. v1.0.0 treats the table below as
the stable v1 reference.

Stable APIs should not change casually. If a signature or return value
changes after v1.0.0, the changelog should call it out plainly and the README
examples should be updated in the same release.

Pre-v1 experimental APIs:

- `st.metric`, `st.bar_chart`, and `st.line_chart` are compact terminal
  summaries, not replacements for plotting libraries.
- `st.container`, `st.columns`, and `st.expander` are grouping primitives, not a
  general layout system.
- `st.table` and `st.dataframe` are static display helpers without editing,
  sorting, or pandas-specific behavior.
- `st.form` and `st.form_submit_button` are small terminal form primitives.
  Pending widget values remain outside `session_state` until submit, but the
  Textual app can still rerun while a form widget is edited.
- `st.status`, `st.spinner`, and `st.help` are simple terminal display
  primitives. They do not promise Streamlit-compatible mutation, animation, or
  full pager-style help behavior.

Explicitly deferred APIs and feature areas:

- `st.sidebar`, `st.tabs`, `st.file_uploader`, `st.cache_data`,
  `st.cache_resource`, and `st.components` are not in the v1 stable API.
- custom column ratios/gaps, editable dataframes, plotting-library parity, and
  browser/server runtime, websocket, or port-forwarding runtime features are
  deferred from v1.

## API Contract Status

v1.0.0 considers the stable public contract documented and frozen for the v1
series.
The current contract lives in [`docs/api-reference.md`](api-reference.md) and
covers:

- Public imports exported from `stui.__all__`.
- Function signatures and return values for text, status, display, widgets,
  forms, grouping, charts, state, and flow-control APIs.
- Callback behavior, `args`/`kwargs`, disabled widgets, explicit keys, generated
  keys, form submit behavior, `st.rerun`, and `st.stop`.
- CLI entry points for running apps, listing/copying bundled examples,
  generating starter files, diagnostics, and version checks.

Experimental APIs may continue to tighten in v1.x, but stable public signature,
return-value, or semantic changes should be treated as compatibility events and
called out in the changelog and release notes.

## Stable And Experimental Status

Stable in v1:

- Text output: `st.title`, `st.header`, `st.subheader`, `st.caption`,
  `st.text`, `st.markdown`, `st.write`, `st.divider`, and `st.code`.
- Basic status output: `st.info`, `st.success`, `st.warning`, `st.error`, and
  `st.exception`.
- Core input widgets: `st.button`, `st.slider`, `st.text_input`, and
  `st.checkbox`.
- `st.session_state` as the core state mapping and attribute proxy.
- CLI commands for running apps, diagnostics, example listing/copying, starter
  generation, and version output.

Experimental in v1:

- `st.status`, `st.spinner`, and `st.help` as terminal status/help primitives
  while their exact grouping and formatting contract gathers feedback.
- `st.json`, `st.progress`, `st.table`, and `st.dataframe` as static display
  helpers whose terminal formatting may still tighten.
- `st.number_input`, `st.selectbox`, and `st.radio` as newer input widgets
  still gathering keyboard and terminal feedback.
- `st.form` and `st.form_submit_button` as small submit-style primitives.
- `st.container` and `st.expander` as terminal grouping/layout primitives.
- `st.rerun` and `st.stop` as flow-control helpers that need real-app
  feedback before being frozen.
- `st.metric`, `st.bar_chart`, and `st.line_chart` as compact terminal
  summaries.
- `st.columns` as a simple responsive terminal primitive. It accepts only an
  integer count and stacks on narrow terminals.
- Wider layout concepts such as sidebars, grids, tabs, custom ratios, or
  responsive layout engines.
- Rich dataframe interactions such as editing, sorting, selection, pagination,
  pandas-specific integrations, or formatting hooks.
- Terminal compatibility claims for environments not yet covered by project
  evidence.

## Stable API

The v1 API should stay compact. These APIs are the stable v1 surface. This table
must match the `v1-stable` rows in `docs/api-stability.md` and
`docs/api-reference.md`:

| Area | APIs |
| --- | --- |
| Text | `st.title`, `st.header`, `st.subheader`, `st.caption`, `st.text`, `st.markdown`, `st.write`, `st.divider`, `st.code` |
| Status | `st.info`, `st.success`, `st.warning`, `st.error`, `st.exception` |
| Inputs | `st.button`, `st.slider`, `st.text_input`, `st.checkbox` |
| State | `st.session_state` |
| Package metadata | `st.__version__` |
| CLI | `stui run`, `stui demo list`, `stui demo NAME`, `stui examples`, `stui example list`, `stui example copy`, `stui init`, `stui doctor`, `stui --version` |

The experimental API is public and documented, but not part of the stable table
yet. Current experimental areas include static display
formatting beyond `st.code`, newer selection and numeric widgets, forms,
grouping/layout helpers, metrics/charts, status/help helpers, and flow-control
helpers.

Every stable API should keep:

- A documented signature and return value.
- Tests for normal behavior, disabled behavior where relevant, callbacks where
  relevant, and stable `key` behavior.
- At least one example or README snippet when the API is user-facing enough to
  need explanation.
- Clear limits when the API is intentionally smaller than a similarly named
  Streamlit API.

## Correctness Gate

v1 should not ship with known state, rerun, or widget identity bugs. The release
checklist must include:

- No known `session_state` loss across normal reruns.
- No known duplicate-key or generated-key collisions in common script shapes.
- Buttons and form submit buttons produce one-shot return values.
- Callbacks run once per user action and receive documented `args`/`kwargs`.
- Widgets preserve user values after rerun, including inside containers, forms,
  and expanders.
- `st.rerun` exits the current script pass cleanly and does not corrupt state.
- `st.stop` exits the current script pass cleanly without showing a traceback.
- Errors from user scripts are visible in the terminal app and do not leave the
  runtime in a misleading state.

## Packaging And Install

v1 must be installable from PyPI as `stui-terminal`:

```bash
python -m pip install stui-terminal
python -m stui --version
stui --version
```

The distribution name remains `stui-terminal`; the import package and CLI remain
`stui`.

The v1 docs should preserve the install and command contract:

```bash
python -m pip install stui-terminal
stui --version
python -m stui --version
stui doctor
stui doctor --json
stui run app.py
python -m stui run app.py
stui examples
stui example list
stui example copy basic ./basic.py
stui example copy counter ./counter.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
stui init ./forms_app.py --template forms
```

The documented starter templates are `basic`, `dashboard`, and `forms`.

The v1 release should verify:

- Clean install in a new virtual environment.
- Editable install for contributors.
- Wheel and source distribution pass `twine check`.
- `python -m stui run ...` works when the `stui` script directory is not on
  `PATH`.
- The installed package exposes examples or an explicit example-copy/listing
  workflow, so users are not forced to clone the repository just to try forms,
  expanders, charts, or the kitchen sink example.

## Examples

The v1 docs should include and test installed or discoverable examples for:

- Basic text, slider, and button behavior.
- Stateful counter with `st.session_state`.
- Inputs: text input, number input, checkbox, selectbox, and radio.
- Data display: table, dataframe, code, JSON, progress, and status messages.
- Forms and submit-button flows.
- Containers and expanders.
- Metrics and terminal-native charts.
- A kitchen sink example that demonstrates the stable API without pretending to
  be a Streamlit compatibility layer.

## Keyboard Documentation

v1.0.0 verifies and documents the current keyboard behavior in the README. v1.x
must keep that documentation current for the default Textual UI:

- `q` quits and `r` manually reruns the script.
- `tab` and `shift+tab` move focus between widgets.
- `enter` activates buttons and form submit buttons.
- Text and number inputs commit edited values with `enter`.
- Checkboxes toggle with `space`; expanders toggle with `enter` or `space`.
- Sliders move with `left`/`right` and `h`/`l`; `home` and `end` jump to
  bounds.
- Selectboxes cycle with arrow keys, and radio groups choose with arrow keys.

The docs should also say which interactions are delegated to Textual defaults
and may vary by terminal.

## Terminal Compatibility

The v1 release notes should state the terminal environments tested for the
release. The project keeps linking users here and asks for structured reports,
but does not claim a finished compatibility matrix. At minimum, v1 should be
checked in:

The working terminal report is tracked in
[`docs/terminal-compatibility.md`](terminal-compatibility.md).

- A modern local macOS terminal.
- A Linux terminal in CI or a clean container.
- A narrow terminal size and a wider terminal size.
- UTF-8 with a normal interactive `TERM`, such as `xterm-256color`.

Known rendering limits should be documented instead of hidden. Wide tables,
large charts, long labels, narrow terminals, and unusual fonts may need
explicit caveats.

Useful terminal reports should include OS, terminal emulator, shell, Python
version, `stui` version, install method, `TERM`, `COLORTERM`, `TERM_PROGRAM`,
terminal size, whether the session is local/SSH/container/headless, and the
output of `stui doctor`.

## CI And Supported Python

The v1 support policy should match CI. The current supported Python line is
Python 3.11, 3.12, and 3.13.

For v1.x:

- CI must pass on every supported Python version.
- The README, `pyproject.toml`, and release notes must agree on supported
  Python versions.
- Dropping a Python version requires a changelog entry and a clear reason.

## Known Limitations To Keep Visible

The README, release notes, and API docs should keep these limits explicit:

- `stui` does not run a browser, local web server, websocket runtime, or
  port-forwarding flow.
- `stui` does not depend on Streamlit at runtime and is not a Streamlit
  compatibility layer.
- Existing Streamlit apps may need edits before they can run with `stui`.
- Static tables/dataframes do not support editing, sorting, or rich dataframe
  integrations.
- Charts are terminal summaries and can lose detail at narrow widths.
- Layout is intentionally modest. `st.columns` is pre-v1 experimental and
  limited to integer-count responsive columns; there are no sidebars, tabs,
  custom layout ratios, arbitrary browser components, or hosted auth features in
  the v1 gate.
- API signatures, callback behavior, disabled behavior, generated-key behavior,
  and form submit semantics are documented as the current contract, and must
  stay synchronized with implementation changes in v1.x.

## Final v1.0 Checklist

| Gate | v1.0.0 status | Post-v1 decision |
| --- | --- | --- |
| Stable API list | Frozen as the v1 stable list. | Do not change unless a correctness, terminal, or safety issue appears. |
| Experimental APIs | Labeled in README, API reference, API stability docs, v1 readiness docs, and tests. | Keep experimental through v1 unless real feedback justifies promotion. |
| Deferred Streamlit-style APIs | Explicitly deferred in API stability docs and README. | Do not add to v1. |
| State/rerun/widget correctness | Covered by regression tests for known issues. | Fix reproducible blockers; document non-blocking limitations. |
| Installed-package flow | Required for v1 release gates. | Verify from PyPI again for every release. |
| Terminal compatibility | Evidence-driven matrix remains open. | Document unknowns instead of overclaiming support. |
| Narrow rendering | Covered by regression tests for known table/chart/layout edges. | Fix reproducible blockers; document non-blocking limitations. |
| Release process | Checklist and publishing docs are explicit. | Follow the same gates for v1.x releases. |
| Public announcement | Prepared for v1.0.0. | Post manually only after PyPI and GitHub release verification. |

## Post-v1 Plan

For every v1.x release:

- Run or collect terminal checks in the environments listed in
  [`docs/terminal-compatibility.md`](terminal-compatibility.md).
- Freeze the public docs against the built artifact before tagging.
- Verify bundled examples, `stui example copy`, and `stui init` from built
  wheel and source artifacts.
- Confirm supported Python versions match CI, README, `pyproject.toml`, and
  release notes.
- Keep experimental APIs labeled until real feedback justifies graduation.
- Keep larger feature requests out of patch releases unless they directly fix a
  reproducible v1 blocker.

## Post-v1 Items

- v1.1: polish the highest-confidence experimental APIs only if real terminal
  feedback shows they are already behaving like stable primitives.
- v1.1: improve docs and examples around installed-package workflows, terminal
  compatibility reports, narrow rendering, and real local/SSH/headless use
  cases.
- v1.2: revisit richer dataframe inspection, chart variants, and layout
  ergonomics only when specific workflows justify them.
- Future: add deprecation warnings and migration notes before removing any
  stable v1 API in a major release.
- Future: keep hosted, browser, cloud, auth, sync, and component-marketplace
  ideas out of scope unless the project intentionally changes direction.

## Release Process

The v1 release process should remain explicit and auditable:

1. Update version metadata, README, changelog, release notes, and v1 readiness
   status.
2. Run local verification: `ruff check .`, `python3.11 -m pytest`,
   `python -m build`, and `python -m twine check dist/*`.
3. Verify examples through `stui run` or `python -m stui run`.
4. Create a tag only after the release diff is final.
5. Publish through GitHub Actions Trusted Publishing with manual dispatch.
6. Verify a clean PyPI install in a temporary virtual environment.
7. Only publish public announcements after PyPI, docs, examples, and CI are
   verified.

Public launch-style announcements should wait for v1.0.0. Pre-1.0 releases can
have release notes, but they should not be framed as the final stable launch.

## Non-Goals For v1

v1 is not a promise to support:

- Streamlit compatibility mode.
- A browser renderer, dashboard server, websocket runtime, or port-forwarding
  workflow.
- Runtime dependency on Streamlit.
- Sidebars, file upload, arbitrary browser components, or hosted auth.
- A large component marketplace or plugin system.
- Full dataframe editing, sorting, or plotting-library replacement behavior.
- GPL widget code or dependencies with licensing that would complicate the
  project.
- Managed cloud deployment, sync, or collaboration features.
