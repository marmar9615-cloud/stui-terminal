# Changelog

All notable changes to this project will be documented in this file.

This project is currently pre-1.0, so APIs may change while the MVP is being
shaped.

## Unreleased

No unreleased changes.

## 0.8.0 - 2026-05-12

### Added

- Added release-candidate hardening notes for the v0.8.0 pre-v1 pass.
- Added installed-package guidance when `stui run examples/<name>.py` is used
  from a directory that does not contain a repository checkout.
- Added CLI regression coverage for the installed-package example-copy hint.
- Added clearer README links to the API reference, API stability labels,
  terminal compatibility matrix, and v1 readiness checklist.

### Changed

- Reaffirmed stable versus pre-v1 experimental API labels in the README, API
  reference, API stability docs, and v1 readiness docs.
- Clarified the public package boundary: install `stui-terminal`, import
  `stui`, run the `stui` CLI, and use `python -m stui` as the fallback entry
  point.
- Updated the v1 readiness and roadmap docs around the v0.8.0
  release-candidate hardening checkpoint and the v0.9.0 final candidate.
- Expanded feedback docs for API-label mismatches, CLI install/init/example
  issues, limitation wording, and v0.9/v1 blockers.
- Refreshed publishing docs to use the v0.8.0 release tag and install
  verification commands.
- Kept public announcement-style launch pushes explicitly saved for v1.0.0.

## 0.7.0 - 2026-05-12

### Added

- Added pre-v1 experimental `st.status(...)`, `st.spinner(...)`, and
  `st.help(...)` primitives for terminal status/help output while their exact
  v1 contract is still gathering feedback.
- Added pre-v1 experimental `st.columns(count)` with simple responsive terminal
  rendering that stacks on narrow terminals.
- Added `docs/layouts.md` to document layout primitives, columns limitations,
  and why tabs remain deferred.
- Added v0.7.0 release notes for the API contract readiness pass.
- Added README links to the API contract status and refreshed terminal
  compatibility guidance.
- Added explicit README non-goals for Streamlit compatibility, browser
  dashboards, hosted/cloud features, plotting/dataframe replacement behavior,
  large component marketplaces, and GPL widget dependencies.

### Changed

- Reframed README API status around v0.7.0 stable-candidate APIs and
  experimental/modest areas.
- Clarified layout primitive status: `st.container`, `st.columns`, and
  `st.expander` are terminal grouping helpers; columns remain pre-v1
  experimental and are not a sidebar, tabs, grid, or full layout engine.
- Expanded examples/init/copy docs with installed-package commands that do not
  require a repository checkout after copying.
- Updated `docs/v1-readiness.md` with API contract status,
  stable/experimental status, remaining blockers, and the v0.8/v0.9 plan.
- Updated `ROADMAP.md` and `docs/feedback.md` around terminal evidence,
  package hardening, API contract mismatch reports, and layout feedback.
- Kept public announcement-style launch pushes explicitly saved for v1.0.0.

## 0.6.0 - 2026-05-12

### Added

- Added v0.6.0 release notes for the compatibility and API-stability readiness
  pass.
- Added README links to the API reference, v1 API stability checklist, and
  terminal compatibility checklist.
- Added clearer feedback asks for terminal reports, keyboard bugs,
  narrow-rendering bugs, API signature confusion, docs gaps, and example gaps.

### Changed

- Reframed README API status around v0.6.0 stable-candidate and experimental
  labels.
- Expanded install, example, and `stui init` docs, including the `python -m
  stui` fallback for environments where the `stui` script is not on `PATH`.
- Updated `docs/v1-readiness.md` with API stability status, known limitations,
  terminal compatibility status, and remaining v1 gates.
- Updated `ROADMAP.md` with the v0.6, v0.7, v0.8, and v1 path.
- Kept public announcement-style launch pushes explicitly saved for v1.0.0.

## 0.5.0 - 2026-05-12

### Added

- Added public `st.stop()` to halt the current script pass without rendering a
  traceback while preserving already-rendered elements and `session_state`.
- Added concise script-focused runtime error formatting for missing files,
  syntax errors, and import errors.
- Added stronger `sys.path` restoration after script runs, including scripts
  that mutate `sys.path` themselves.
- Added `stui example list` and starter templates for
  `stui init --template basic|dashboard|forms`.
- Added `docs/terminal-compatibility.md` with an honest terminal matrix and
  bug-reporting checklist.
- Added clearer feedback requests for terminal reports, keyboard issues,
  install/package problems, API confusion, and desired examples.

### Changed

- Improved keyboard behavior and help text for selectbox, radio, expander, and
  slider controls.
- Expanded `stui doctor` with terminal size status, `TERM`, `COLORTERM`, TTY
  status for stdin/stdout/stderr, color capability, theme, dependency versions,
  and small-terminal warnings.
- Improved `stui examples` output with descriptions, bundled/repo source
  labels, and exact copy/run commands.
- Updated README install, 60-second quickstart, first app, CLI commands, API
  table, keyboard shortcuts, terminal compatibility link, limitations, and v1
  roadmap.
- Updated `docs/v1-readiness.md` with the post-v0.5.0 status and the remaining
  v1 gates.
- Updated `ROADMAP.md` with the v0.5, v0.6, v0.7, and v1 path.
- Kept public announcement-style launch pushes explicitly saved for v1.0.0.

## 0.4.0 - 2026-05-12

### Added

- Added `st.line_chart` as a compact static sparkline helper for numeric lists
  and dictionaries of numeric series.
- Added keyboard-toggleable `st.expander` state with explicit/generated keys.
- Added bundled package examples plus `stui example copy` and `stui init`.
- Added `docs/v1-readiness.md` for the path from pre-1.0 releases to a stable
  v1 API.

### Changed

- Deferred form widget values from `session_state` until
  `st.form_submit_button` commits the form, while preserving current displayed
  pending values across reruns.
- Form widget callbacks now run after submit commit and before the submitted
  script branch continues.
- Hardened `st.bar_chart` rendering for negative values, zero-only data,
  non-finite values, clearer labels, and small chart widths.
- Improved `stui doctor` example diagnostics and installed-package guidance.
- Strengthened static policy checks around publish artifacts and trusted
  publishing.

## 0.3.0 - 2026-05-12

### Added

- Form primitives: `st.form` and `st.form_submit_button`.
- Grouping primitives: `st.container` and static `st.expander`.
- Terminal display primitives: `st.metric` and `st.bar_chart`.
- High-contrast theme support through `STUI_THEME=high-contrast`.
- Examples for forms, grouping/layouts, charts, and the expanded kitchen sink.
- Tests for forms, grouping, metric/chart rendering, and theme behavior.

### Changed

- Expanded `stui doctor` with terminal size and resolved theme details.
- Updated README, roadmap, feedback docs, release notes, and examples for
  the v0.3.0 terminal-app primitives release.

## 0.2.2 - 2026-05-09

### Changed

- Replaced the generated SVG preview with a real terminal screenshot captured
  from `stui run examples/model_demo.py`.
- Switched the README preview image to a versioned raw GitHub URL so it renders
  correctly on PyPI.
- Kept the runtime API and behavior unchanged from 0.2.1.

## 0.2.1 - 2026-05-09

### Changed

- Prepared a polish and metadata patch for the public 0.2.x release line.
- Refreshed release notes, announcement copy, and publishing references for
  `stui-terminal` v0.2.1.
- Kept the runtime API and behavior unchanged from 0.2.0.

## 0.2.0 - 2026-05-09

### Added

- Display helpers: `subheader`, `caption`, `code`, `json`, `exception`, and
  `progress`.
- Input helpers: `number_input`, `selectbox`, and `radio`.
- Data display helpers: `table` and `dataframe` without a pandas dependency.
- CLI diagnostics with `stui doctor` and example discovery with
  `stui examples`.
- Example apps for inputs, data display, and a compact dashboard.

### Changed

- Promoted the 0.2.0 release line from release candidate to stable.
- Refreshed public docs for the `stui-terminal` install path, compact API
  reference, troubleshooting, and stable announcement copy.

## 0.2.0rc1 - 2026-05-09

### Added

- Release candidate for the 0.2.0 API expansion.

## 0.1.0rc2 - 2026-05-09

### Changed

- Updated install documentation for the future PyPI distribution name,
  `stui-terminal`.
- Clarified that the distribution name is `stui-terminal`, while the import
  package and CLI remain `stui`.
- Preserved editable local development install instructions for contributors.

## 0.1.0rc1 - 2026-05-08

### Added

- Initial terminal-native `stui` MVP with top-to-bottom script reruns.
- Public APIs for text output, alerts, button, slider, text input, checkbox,
  and session state.
- Textual terminal renderer with keyboard-first widget interactions.
- CLI entrypoints for `stui run ...` and `python -m stui run ...`.
- Example apps for the basic demo, counter, and model-parameter playground.
- Test suite, static policy checks, CI workflow, contributor guide, and release
  candidate documentation.
