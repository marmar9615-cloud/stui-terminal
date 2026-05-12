# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## v0.9 Final v1-Candidate Closeout

- Keep the v1 candidate API list frozen unless a documented correctness,
  terminal, or security issue forces a change.
- Treat the API reference as the current public contract: signatures, return
  values, callbacks, `args`/`kwargs`, generated and explicit `key` behavior,
  disabled behavior, form submit behavior, `st.rerun`, and `st.stop`.
- Ensure every stable-candidate API has focused tests and at least one README,
  example, or reference-doc mention.
- Scope layout primitives honestly: `st.container`, `st.columns`, and
  `st.expander` are terminal grouping helpers, not sidebars, tabs, browser
  grids, or a full layout engine. `st.columns` remains pre-v1 experimental.
- Keep charts and richer dataframe behavior experimental or explicitly modest
  until real v1 feedback says they should graduate.
- Keep release notes, changelog, README, feedback docs, and v1 readiness docs
  aligned without generating public launch posts.

## v0.9 Release Gates

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

The stable-candidate API is the top-level `stui` surface marked `v1-stable` in
[`docs/api-stability.md`](docs/api-stability.md). These names should keep their
call shape and core behavior through v1.0.0 unless a correctness
issue forces a change.

The pre-v1 experimental API is still public enough to try, but the project is
asking for feedback before freezing it. This includes newer display helpers,
tables/dataframes, charts, forms, selection widgets, layout/grouping helpers,
status/help helpers, and flow-control helpers that need more real terminal
evidence before v1.

The command surface is expected to remain stable for v1 docs:

- `stui run APP.py`
- `python -m stui run APP.py`
- `stui examples`
- `stui example list`
- `stui example copy NAME DEST`
- `stui init APP.py --template basic|dashboard|forms`
- `stui doctor`
- `stui doctor --json`
- `stui --version`

## Layout Criteria Before Expansion

- `st.columns` must keep passing focused runtime/rendering tests for child order,
  nesting, wide rendering, and narrow stacking.
- Terminal reports should show readable behavior in at least one local macOS
  terminal and one Linux or SSH/headless-style environment before promoting
  columns beyond pre-v1 experimental.
- Do not add tabs until keyboard navigation, hidden-content state semantics, and
  generated widget keys are predictable enough to document.
- Do not add sidebars, custom ratios, browser-grid behavior, or horizontal
  scrolling unless a real terminal workflow cannot be expressed with headings,
  containers, columns, and expanders.

## v1 Stable Release

- Ship the documented small API surface only once there are no known state/rerun
  correctness bugs or every remaining issue is explicitly deferred.
- Treat the APIs in `docs/v1-readiness.md` as the v1 stability candidate until
  the project intentionally adds or removes an item.
- Verify PyPI install, built artifacts, examples/init/copy commands, docs, CI,
  and terminal compatibility evidence together before calling v1 complete.
- Keep Python support aligned with CI and document any support changes in the
  changelog.
- Keep the package install path stable: PyPI distribution `stui-terminal`,
  import package `stui`, and CLI command `stui`.
- Publish public launch announcements only after v1.0.0 is released, install
  verified from PyPI, and the docs/examples match the shipped package. The
  public announcement push is saved for v1.0.0.

## Post-v1 Candidates

- Promote experimental APIs only after real terminal feedback supports their
  current behavior.
- Revisit richer dataframe interactions, chart variants, tabs, sidebars, and
  broader layout primitives after the v1 API has settled.
- Expand terminal compatibility evidence across more terminals and operating
  systems without overstating unverified environments.
- Add normal deprecation warnings and migration notes before removing stable v1
  APIs in a future major release.

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
  for a real terminal app before v1.
- Whether the terminal UI behaved well with your shell, font, theme, and
  terminal emulator.
- Where keyboard or mouse behavior made the app feel slower than a script or a
  browser dashboard.
- Which examples or docs would have made the first run clearer.
