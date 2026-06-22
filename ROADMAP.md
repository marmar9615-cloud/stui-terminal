# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## v1 Stable Baseline

- Keep the v1 stable API list frozen unless a documented correctness,
  terminal, or security issue forces a change.
- Treat the API reference as the current public contract: signatures, return
  values, callbacks, `args`/`kwargs`, generated and explicit `key` behavior,
  disabled behavior, form submit behavior, `st.rerun`, and `st.stop`.
- Ensure every stable API has focused tests and at least one README,
  example, or reference-doc mention.
- Scope layout primitives honestly: `st.container`, `st.expander`, and
  count-only `st.columns` are terminal grouping helpers, not sidebars, tabs,
  browser grids, or a full layout engine.
- Keep charts compact and terminal-native. `st.bar_chart` and `st.line_chart`
  are stable summaries for documented numeric shapes; richer chart variants and
  plotting-library parity remain future work.
- Keep release notes, changelog, README, feedback docs, and v1 readiness docs
  aligned with the shipped package.

## v1 Maintenance Gates

- Verify terminal compatibility across supported Python versions and common
  environments: macOS terminals, Linux terminals or containers, SSH/headless
  sessions, narrow and wide terminal sizes, UTF-8, and normal interactive
  `TERM` values.
- Polish or document narrow-width behavior for tables, charts, forms, grouped
  content, long labels, and help text.
- Confirm error display and recovery when user scripts raise exceptions.
- Re-run install and example smoke checks against built artifacts, not only an
  editable checkout.
- Verify clean PyPI-style installs, editable installs, bundled example copying,
  `stui init`, source distribution, wheel, and `twine check`.
- Keep `st.columns` intentionally small: integer count only, responsive stacking
  on narrow terminals, and documented limitations. Do not add ratios, tabs,
  sidebars, grids, or a broader layout engine without terminal evidence and a
  concrete user workflow.
- Keep `st.empty()` deferred until placeholder mutation semantics are clear in
  the rerun-based terminal runtime. A static placeholder that does not update
  would be misleading.
- Defer larger features such as richer dataframe interactions, table selection,
  chart variants, tabs, sidebars, or layout expansion unless real v1 feedback
  shows a clear need.

## Stable Versus Experimental API Boundary

The stable API is the top-level `stui` surface marked `v1-stable` in
[`docs/api-stability.md`](docs/api-stability.md). These names should keep their
call shape and core behavior through v1.x unless a correctness
issue forces a change.

The experimental API is still public enough to try, but the project is asking
for feedback before freezing it. In v1.5.0 the remaining experimental APIs are
`st.status`, `st.spinner`, and `st.help`.

The command surface is expected to remain stable for v1 docs:

- `stui run APP.py`
- `python -m stui run APP.py`
- `stui demo list`
- `stui demo NAME`
- `stui examples`
- `stui example list`
- `stui example copy NAME DEST`
- `stui init APP.py --template basic|dashboard|forms`
- `stui doctor`
- `stui doctor --json`
- `stui doctor --compat`
- `stui selftest`
- `stui selftest --json`
- `stui --version`

## Layout Criteria Before Expansion

- `st.columns` must keep passing focused runtime/rendering tests for child order,
  nesting, wide rendering, and narrow stacking.
- Terminal reports should show readable behavior in at least one local macOS
  terminal and one Linux or SSH/headless-style environment before expanding
  columns beyond count-only behavior.
- Do not add tabs until keyboard navigation, hidden-content state semantics, and
  generated widget keys are predictable enough to document.
- Do not add sidebars, custom ratios, browser-grid behavior, or horizontal
  scrolling unless a real terminal workflow cannot be expressed with headings,
  containers, columns, and expanders.

## v1.x Release Discipline

- Treat the documented small API surface as the v1 stable contract unless the
  project intentionally adds, graduates, or deprecates an item in a documented
  release.
- Verify PyPI install, built artifacts, examples/init/copy commands, docs, CI,
  package contents, custom external projects, and terminal compatibility
  evidence together before calling routine v1.x releases complete.
- Keep Python support aligned with CI and document any support changes in the
  changelog.
- Keep the package install path stable: PyPI distribution `stui-terminal`,
  import package `stui`, and CLI command `stui`.
- For routine v1.x releases, write changelog and GitHub Release notes only. Do
  not generate social launch copy unless it is explicitly requested.

## v1.1 Shipped

- Graduated the safest post-v1 APIs: static JSON/progress/table/dataframe
  display, numeric and choice inputs, forms, containers, expanders, metrics, and
  explicit flow control.
- Hardened generated-key collision checks, form callback commit timing, progress
  validation, JSON display fallbacks, and installed-user CLI diagnostics.
- Improved installed-package examples, `stui init` templates, and terminal
  compatibility docs based on early v1 feedback.
- Tightened narrow-width rendering and keyboard documentation where reports show
  reproducible friction.
- Keep patch releases boring: bugs, docs, examples, packaging, and compatibility
  evidence.

## v1.2 Shipped

- Added `stui check APP.py` and `stui check APP.py --json` for
  non-interactive app validation in local scripts and CI.
- Added a repeatable custom external-project validation script that creates an
  app outside the repository and checks local imports plus rendered element
  summaries.
- Added stable `max_rows` and `max_cols` keyword limits for `st.table` and
  `st.dataframe`, including visible `+N rows` and `+N cols` markers.
- Improved dataframe-like empty-record handling so declared columns are
  preserved without requiring pandas.
- Hardened chart empty states so unsupported or all-invalid data renders as
  `No chart data` instead of a misleading zero value.
- Graduated count-only `st.columns(count)` to stable while keeping ratios, tabs,
  sidebars, and larger layout systems deferred.

## v1.3 Shipped

- Added `stui selftest` and `stui selftest --json` for lightweight
  installed-package validation without launching the full Textual UI.
- Added a repeatable package-contents audit script for wheel/sdist hygiene.
- Kept stale social launch drafts out of source distributions.
- Aligned the README/PyPI screenshot path with a real bundled `model_demo`
  command.
- Added a docs index and cleaned stale post-v1 wording.

## v1.4 Shipped

- Graduated `st.bar_chart` and `st.line_chart` as stable compact terminal
  summaries for documented numeric shapes.
- Added tuple-pair and dict-of-columns chart data support for common
  script-friendly inputs.
- Added `stui doctor --compat` and richer doctor JSON compatibility fields for
  terminal reports.
- Updated chart examples, docs, and regression tests around narrow,
  signed-value, unsupported, and column-shaped inputs.

## v1.5 Shipped

- Improved `st.table` and `st.dataframe` static display for dataclasses,
  namedtuples, simple public objects, uneven rows, empty tables, multiline cells,
  and `max_cols` markers in narrow terminals.
- Refined count-only `st.columns` so nested column groups stack according to
  their parent column width.
- Updated bundled data/layout examples and docs around installed-user copy/run
  flows, static-table limitations, and modest layout patterns.

## v1.6+ Candidates

- Revisit additional chart variants and richer static data inspection if users
  are building real terminal dashboards that need them.
- Explore table formatting hooks or lightweight selection only if they can stay
  terminal-native and dependency-light.
- Reassess status, spinner, and help after they have enough v1 usage to either
  stabilize or redesign.
- Continue expanding compatibility evidence across macOS, Linux, SSH/headless,
  editor terminals, containers, and Windows setups without overstating
  environments the project has not tested.

## Future Direction

- Add normal deprecation warnings and migration notes before removing stable v1
  APIs in a future major release.
- Consider a small extension story only after the core API has proven stable in
  real terminal apps.
- Keep large hosted, browser, cloud, auth, sync, and component-marketplace ideas
  out of scope unless the project intentionally changes direction.

## Not Planned Yet

- Streamlit compatibility mode.
- A browser renderer, dashboard server, websocket runtime, or port-forwarding
  workflow.
- A large built-in component catalog before the core API has settled.
- Runtime dependency on Streamlit.
- GPL widget code or dependencies with licensing that would complicate the
  project.
- Hosted auth, cloud sync, or managed deployment features.

## Feedback Areas

The most useful feedback is specific and tied to a real terminal workflow:

- Which local, SSH, headless, data, model, or DevOps task you tried to build.
- Which API felt natural, confusing, too small, or too surprising.
- Which widget or display primitive blocked the app from being useful.
- Whether forms, containers, expanders, metrics, or charts are expressive enough
  for a real terminal app in the v1 series.
- Whether the terminal UI behaved well with your shell, font, theme, and
  terminal emulator.
- Where keyboard or mouse behavior made the app feel slower than a script or a
  browser dashboard.
- Which examples or docs would have made the first run clearer.
