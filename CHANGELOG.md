# Changelog

All notable changes to this project will be documented in this file.

This project is currently pre-1.0, so APIs may change while the MVP is being
shaped.

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
