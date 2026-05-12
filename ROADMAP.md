# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## v0.5 Developer Experience And Docs

- Ship README clarity for install, 60-second quickstart, first app, CLI
  commands, API status, keyboard shortcuts, terminal compatibility, limitations,
  and the v1 path.
- Keep v0.5 release notes, changelog, feedback docs, and v1 readiness docs
  aligned with the package boundary: small API, terminal-native runtime, and no
  Streamlit compatibility claim.
- Make feedback requests more specific: terminal reports, keyboard issues,
  install/package problems, API confusion, and examples users want before v1.
- Preserve the announcement gate: public launch-style pushes are saved for
  v1.0.0, not v0.5.0.

## v0.6 Terminal Compatibility And Polish

- Verify terminal compatibility across supported Python versions and common
  environments: macOS terminals, Linux terminals or containers, SSH/headless
  sessions, narrow and wide terminal sizes, UTF-8, and normal interactive
  `TERM` values.
- Polish narrow-width behavior for tables, charts, forms, grouped content, and
  long labels.
- Stabilize error display and recovery when user scripts raise exceptions.
- Improve `stui doctor` output when terminal size, theme, `TERM`, color
  capability, TTY status, or install path issues are likely to affect rendering.
- Revisit dataframe display, table selection, chart variants, `st.columns`, and
  richer layout only where real workflows show a clear need.

## v0.7 Release Candidate Cleanup

- Freeze the v1 candidate API list and document signatures, return values,
  callbacks, `key` behavior, disabled behavior, and intentional differences from
  Streamlit.
- Ensure every stable candidate API has a README or example path and focused
  tests.
- Verify clean PyPI-style installs, editable installs, bundled example copying,
  source distribution, wheel, and `twine check`.
- Finalize the v1 release checklist, terminal compatibility report format, and
  changelog/release-note expectations.

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
