# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## v0.4 Correctness And Interactions

- Shipped deferred form `session_state` commits, keyboard-toggleable expanders,
  chart hardening, `st.line_chart`, bundled examples, `stui example copy`, and
  `stui init`.
- Remaining v0.4 feedback should focus on whether these corrected semantics are
  enough before the v1 API freeze.

## v0.5 DX And Docs

- Expand keyboard documentation for every interactive widget.
- Add clearer example walkthroughs for local tools, SSH sessions, data scripts,
  model/debug panels, and DevOps dashboards.
- Improve `stui doctor` output when terminal size, theme, `TERM`, or install
  path issues are likely to affect rendering.
- Add screenshot or GIF documentation using real terminal output.
- Make API reference docs explicit about signatures, return values, callbacks,
  `key` behavior, and intentional differences from Streamlit.

## v0.6 Compatibility And Polish

- Verify terminal compatibility across the supported Python versions and common
  terminal environments.
- Polish narrow-width behavior for tables, charts, forms, and grouped content.
- Stabilize error display and recovery when user scripts raise exceptions.
- Revisit dataframe display, table selection, chart variants, `st.columns`, and
  richer layout only where real workflows show a clear need.
- Prepare the release process, checklist, and PyPI verification path for a v1
  release candidate.

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
  verified from PyPI, and the docs/examples match the shipped package.

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
