# v1 Readiness

`stui` v2.2.0 is the current release target; v2.0.0 was the first v2 stable
release and v2.1.0 was the first post-v2 feature release.
The goal for the v1 series is not to become Streamlit-compatible or to grow a
large component catalog. The goal is a small, stable, terminal-native API that
can be installed from PyPI, explained quickly, and trusted for local tools.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Status After v2.0.0

v2.0.0 keeps the v1.0.0 baseline intact and preserves v1.4.0 through v1.9.0
behavior while publishing the v2.0.0 stable contract in
[`docs/v2-readiness.md`](v2-readiness.md). It is intentionally a contract,
documentation, packaging, and release-proof milestone rather than a risky
feature wave.

The release keeps the remaining `st.status`, `st.spinner`, and `st.help` APIs
post-v1 experimental.

On the v1.x line, the stable API list is frozen. The freeze covers the
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

Normal v1.x release work should include changelog and GitHub Release notes only.
Do not generate social launch copy for maintenance or minor releases unless a
separate task explicitly asks for it.

## Complete Through v2.0.0

- The PyPI distribution/import/CLI naming is settled: install
  `stui-terminal`, import `stui`, and run `stui`.
- The stable API is documented in the README, API reference, API
  stability table, and public API tests.
- v1.2.0 kept the v1.1 stable API intact, added stable table/dataframe
  `max_rows` and `max_cols` output limits, and graduated count-only
  `st.columns(count)`.
- `stui check APP.py` provides a non-interactive runtime validation command for
  local and CI use; `--strict` fails on authoring warnings such as scripts that
  render no visible elements.
- `stui selftest` provides a lightweight installed-package health check for
  bundled examples, templates, package metadata, and non-interactive runtime
  validation; `--strict` checks every bundled example and init template, and
  `--repeat` reruns those checks to catch accumulation issues.
- `scripts/audit_package_contents.py` verifies wheel/sdist contents and keeps
  stale package files out of release artifacts; `--version` verifies artifact
  filenames and metadata against the intended release.
- `st.bar_chart` and `st.line_chart` are stable compact terminal summaries for
  documented numeric shapes, including tuple pairs and dict-of-columns inputs.
- `st.table` and `st.dataframe` cover common static data shapes, including
  dataclasses, namedtuples, simple public objects, dict-of-lists, uneven rows,
  empty tables, and `max_rows`/`max_cols` markers.
- Count-only `st.columns` stays stable and now stacks nested column groups using
  the parent column width.
- `st.status`, `st.spinner`, and `st.help` have explicit example coverage in the
  kitchen-sink app and tests for collapsed status children, nested grouping,
  default spinner text, documented states, and simple help formatting.
- `stui doctor --json` and `stui doctor --compat` make unsupported themes and
  `NO_COLOR` diagnostics easier to paste into terminal compatibility reports.
- `scripts/check_release_version.py` verifies that release metadata and tag names
  agree before publishing.
- `stui init` now includes `basic`, `dashboard`, `data`, `charts`, and `forms`
  templates for installed users.
- `stui check --repeat` validates repeated script passes in one runtime and
  reports per-run element/error/warning summaries in JSON.
- Authoring errors, hidden form fields, and rerun storms have focused rollback
  regression tests.
- Disabled form widgets and empty choice widgets inside forms have focused
  deferred-state regression tests.
- Remaining experimental APIs stay labeled instead of being quietly promoted.
- Deferred Streamlit-style features are listed as out of scope for v1.
- The README quickstart, first app, API table, terminal compatibility link,
  examples/templates, limitations, and troubleshooting sections all point users
  at the same v2.0.0 contract.
- Bundled demo/example listing/copying and `stui init` are part of the v1
  documentation contract rather than checkout-only conveniences.

## Post-v1 Verification Habits

- Re-run the full release checklist against exact release artifacts for every
  patch/minor release, not only the editable checkout.
- Verify PyPI install from a clean virtual environment after publish.
- Keep the terminal compatibility matrix evidence-driven and leave unsupported
  environments labeled unknown or test-needed.
- Confirm PyPI/GitHub screenshots and docs still represent real shipped apps.

## API Stability Status

The project should keep the public API small. v2.0.0 treats the table below as
the stable v1 reference and the v2.0.0 stable contract.

Stable APIs should not change casually. If a signature or return value
changes after v1.0.0, the changelog should call it out plainly and the README
examples should be updated in the same release.

Post-v1 experimental APIs:

- `st.status`, `st.spinner`, and `st.help` are simple terminal display
  primitives. They do not promise Streamlit-compatible mutation, animation, or
  full pager-style help behavior.

Explicitly deferred APIs and feature areas:

- `st.sidebar`, `st.tabs`, `st.file_uploader`, `st.components`, and `st.empty`
  are not in the v1 stable API. `st.cache_data` and `st.cache_resource` arrived
  after v2 as experimental APIs and are not retroactively part of the v1
  contract.
- custom column ratios/gaps, editable dataframes, plotting-library parity, and
  browser/server runtime, websocket, or port-forwarding runtime features are
  deferred from v1.

## API Contract Status

v2.0.0 considers the stable public contract documented and frozen for the v1
series.
The current contract lives in [`docs/api-reference.md`](api-reference.md) and
covers:

- Public imports exported from `stui.__all__`.
- Function signatures and return values for text, status, display, widgets,
  forms, grouping, charts, state, and flow-control APIs.
- Callback behavior, `args`/`kwargs`, disabled widgets, explicit keys, generated
  keys, form submit behavior, `st.rerun`, and `st.stop`.
- CLI entry points for running apps, listing/copying bundled examples,
  generating starter files, diagnostics, self-tests, and version checks.

Post-v1 experimental APIs may continue to tighten in v1.x, but stable public
signature, return-value, or semantic changes should be treated as compatibility
events and called out in the changelog and release notes.

## Stable And Experimental Status

Stable in v1:

- Text output: `st.title`, `st.header`, `st.subheader`, `st.caption`,
  `st.text`, `st.markdown`, `st.write`, `st.divider`, and `st.code`.
- Basic status output: `st.info`, `st.success`, `st.warning`, `st.error`, and
  `st.exception`.
- Static display: `st.json`, `st.progress`, `st.table`, `st.dataframe`, and
  `st.metric`, `st.bar_chart`, and `st.line_chart`.
- Input widgets: `st.button`, `st.slider`, `st.text_input`, `st.checkbox`,
  `st.number_input`, `st.selectbox`, and `st.radio`.
- Forms, grouping, and layout: `st.form`, `st.form_submit_button`,
  `st.container`, `st.expander`, and `st.columns`.
- `st.session_state` as the core state mapping and attribute proxy.
- `st.rerun` and `st.stop` as explicit flow-control helpers.
- `st.__version__` as package version metadata.
- CLI commands for running apps, diagnostics, example listing/copying, starter
  generation, and version output.

Experimental in v1:

- `st.status`, `st.spinner`, and `st.help` as terminal status/help primitives
  while their exact grouping and formatting contract gathers feedback.
- Larger layout systems such as sidebars, grids, tabs, custom ratios, or
  browser-style responsive layout engines.
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
| Display | `st.json`, `st.progress`, `st.table`, `st.dataframe`, `st.metric`, `st.bar_chart`, `st.line_chart` |
| Inputs | `st.button`, `st.slider`, `st.text_input`, `st.checkbox`, `st.number_input`, `st.selectbox`, `st.radio` |
| Forms and grouping | `st.form`, `st.form_submit_button`, `st.container`, `st.expander`, `st.columns` |
| State and flow | `st.session_state`, `st.rerun`, `st.stop` |
| Package metadata | `st.__version__` |
| CLI | `stui run`, `stui check`, `stui demo list`, `stui demo NAME`, `stui examples`, `stui example list`, `stui example copy`, `stui init`, `stui doctor`, `stui --version` |

The experimental API is public and documented, but not part of the stable table
yet. Current experimental areas are `st.status`, `st.spinner`, and `st.help`,
plus larger deferred layout systems, plotting-library parity,
dataframe-editing, caching, file-upload, and browser/server runtime areas.

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
stui check app.py
stui check app.py --json
stui check app.py --strict
stui selftest --strict
stui run app.py
python -m stui run app.py
stui examples
stui example list
stui example copy basic ./basic.py
stui example copy counter ./counter.py
stui init ./new_app.py
stui init ./dashboard.py --template dashboard
stui init ./data_app.py --template data
stui init ./charts_app.py --template charts
stui init ./forms_app.py --template forms
```

The documented starter templates are `basic`, `dashboard`, `data`, `charts`,
and `forms`.

The v1 release should verify:

- Clean install in a new virtual environment.
- Editable install for contributors.
- Wheel and source distribution pass `twine check`.
- `python -m stui run ...` works when the `stui` script directory is not on
  `PATH`.
- `stui check APP.py --strict` works from outside a repository checkout and
  returns structured JSON for CI use.
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
- Layout is intentionally modest. `st.columns` is stable but limited to
  integer-count responsive columns; there are no sidebars, tabs, custom layout
  ratios, arbitrary browser components, or hosted auth features in the v1 gate.
- API signatures, callback behavior, disabled behavior, generated-key behavior,
  and form submit semantics are documented as the current contract, and must
  stay synchronized with implementation changes in v1.x.

## v1.x Release Checklist

| Gate | v2.0.0 status | v1.x decision |
| --- | --- | --- |
| Stable API list | Includes bounded tables/dataframes, count-only columns, and compact terminal charts. | Do not change unless a correctness, terminal, or safety issue appears. |
| Experimental APIs | Labeled in README, API reference, API stability docs, v1 readiness docs, and tests. | Keep experimental until tests, docs, and terminal evidence justify promotion. |
| Deferred Streamlit-style APIs | Explicitly deferred in API stability docs and README. | Do not add to v1. |
| State/rerun/widget correctness | Covered by regression tests for known issues, including authoring-error rollback, hidden form pending values, and rerun exhaustion. | Fix reproducible blockers; document non-blocking limitations. |
| Installed-package flow | Required for v1 release gates, now including repeated `stui selftest --strict --repeat 2` and `stui check --strict --repeat 2`. | Verify from PyPI again for every release. |
| Terminal compatibility | Evidence-driven matrix remains open. | Document unknowns instead of overclaiming support. |
| Narrow rendering | Covered by regression tests for known table/chart/layout edges. | Fix reproducible blockers; document non-blocking limitations. |
| Release process | Checklist and publishing docs are explicit. | Follow the same gates for v1.x releases. |
| Public announcement | Not part of v2.0.0 in this release train. | Generate no social or discussion copy for routine releases unless explicitly requested. |

## Post-v1 Plan

For every v1.x release:

- Run or collect terminal checks in the environments listed in
  [`docs/terminal-compatibility.md`](terminal-compatibility.md).
- Freeze the public docs against the built artifact before tagging.
- Verify bundled examples, `stui example copy`, and `stui init` from built
  wheel and source artifacts.
- Confirm supported Python versions match CI, README, `pyproject.toml`, and
  release notes.
- Keep experimental APIs labeled until tests, docs, and feedback justify graduation.
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
7. For routine v1.x releases, write changelog and GitHub Release notes only;
   do not generate social launch copy unless explicitly requested.

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
