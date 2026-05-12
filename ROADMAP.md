# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## v0.6 Compatibility And API Stability

- Align the README with the v1 readiness docs: API reference link, terminal
  compatibility link, install flow, repository examples, bundled example
  copying, and `stui init` templates.
- Label the API surface as stable-candidate or experimental before v1. Text,
  status, input, state, flow, forms, grouping, CLI, and static display helpers
  should remain small and documented.
- Keep experimental claims modest for charts, dataframe/table behavior, and
  layout/grouping primitives.
- Update release notes, changelog, feedback docs, and v1 readiness docs around
  terminal reports, keyboard bugs, narrow rendering, API signature confusion,
  docs gaps, and example requests.
- Preserve the announcement gate: public launch-style pushes are saved for
  v1.0.0, not v0.6.0.

## v0.7 API Reference And Release Candidate Prep

- Freeze the v1 candidate API list unless a documented issue forces a change.
- Document signatures, return values, callbacks, `args`/`kwargs`, generated and
  explicit `key` behavior, disabled behavior, form submit behavior, `st.rerun`,
  and `st.stop`.
- Ensure every stable-candidate API has focused tests and at least one README,
  example, or reference-doc mention.
- Verify clean PyPI-style installs, editable installs, bundled example copying,
  `stui init`, source distribution, wheel, and `twine check`.
- Finalize release-candidate checklist, terminal report format, and
  changelog/release-note expectations.

## v0.8 Terminal Evidence And Hardening

- Verify terminal compatibility across supported Python versions and common
  environments: macOS terminals, Linux terminals or containers, SSH/headless
  sessions, narrow and wide terminal sizes, UTF-8, and normal interactive
  `TERM` values.
- Polish or document narrow-width behavior for tables, charts, forms, grouped
  content, long labels, and help text.
- Confirm error display and recovery when user scripts raise exceptions.
- Re-run install and example smoke checks against built artifacts, not only an
  editable checkout.
- Defer larger features such as richer dataframe interactions, table selection,
  chart variants, columns, or layout expansion unless real v1 feedback shows a
  clear need.

## v1 Stable API

- Freeze the documented small API surface once there are no known state/rerun
  correctness bugs.
- Treat the APIs in `docs/v1-readiness.md` as the v1 stability candidate until
  the project intentionally adds or removes an item.
- Keep Python support aligned with CI and document any support changes in the
  changelog.
- Keep the package install path stable: PyPI distribution `stui-terminal`,
  import package `stui`, and CLI command `stui`.
- Publish public launch announcements only after v1.0.0 is released, install
  verified from PyPI, and the docs/examples match the shipped package. The
  public announcement push is saved for v1.0.0.

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
