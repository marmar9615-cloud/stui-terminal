# v1 Readiness

`stui` is pre-1.0. The goal for v1 is not to become Streamlit-compatible or to
grow a large component catalog. The goal is a small, stable, terminal-native API
that can be installed from PyPI, explained quickly, and trusted for local tools.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Status After v0.6.0

v0.6.0 is a compatibility and API-stability checkpoint, not the v1 API freeze.
It aligns the README, roadmap, feedback asks, release notes, and changelog
around the small public surface that is most likely to become v1.

The v1 gate remains open. Before v1.0.0, the project still needs a terminal
compatibility evidence pass, narrow-width polish, final API signature docs,
package verification, and release-candidate checks against the shipped PyPI
artifact.

Public launch-style announcement pushes are saved for v1.0.0, after the stable
API, PyPI install path, examples, docs, CI, and terminal compatibility checks
are verified together.

## API Stability Status

The project should keep the public API small. v0.6.0 treats the table below as
the candidate v1 reference, while still allowing corrections before the release
candidate line.

Stable-candidate APIs should not change casually. If a signature or return value
changes after v0.6.0, the changelog should call it out plainly and the README
examples should be updated in the same release.

Experimental or intentionally modest areas:

- `st.metric`, `st.bar_chart`, and `st.line_chart` are compact terminal
  summaries, not replacements for plotting libraries.
- `st.container` and `st.expander` are grouping primitives, not a general layout
  system.
- `st.table` and `st.dataframe` are static display helpers without editing,
  sorting, or pandas-specific behavior.
- `st.form` and `st.form_submit_button` are small terminal form primitives.
  Pending widget values remain outside `session_state` until submit, but the
  Textual app can still rerun while a form widget is edited.

## Stable API Candidate

The v1 API should stay compact. These APIs are candidates for the stable v1
surface once their behavior is documented and covered by tests:

| Area | APIs |
| --- | --- |
| Text | `st.title`, `st.header`, `st.subheader`, `st.caption`, `st.text`, `st.markdown`, `st.write`, `st.divider` |
| Status | `st.info`, `st.success`, `st.warning`, `st.error`, `st.exception` |
| Display | `st.code`, `st.json`, `st.progress`, `st.table`, `st.dataframe` |
| Inputs | `st.button`, `st.slider`, `st.text_input`, `st.checkbox`, `st.number_input`, `st.selectbox`, `st.radio` |
| Forms | `st.form`, `st.form_submit_button` |
| Grouping | `st.container`, `st.expander` |
| Metrics and charts | `st.metric`, `st.bar_chart`, `st.line_chart` |
| State and flow | `st.session_state`, `st.rerun`, `st.stop` |
| CLI | `stui run`, `stui examples`, `stui example list`, `stui example copy`, `stui init`, `stui doctor`, `stui --version` |

Before v1, every stable API must have:

- A documented signature and return value.
- Tests for normal behavior, disabled behavior where relevant, callbacks where
  relevant, and stable `key` behavior.
- At least one example or README snippet when the API is user-facing enough to
  need explanation.
- Clear limits when the API is intentionally smaller than a similarly named
  Streamlit API.

## Correctness Gate

v1 should not ship with known state, rerun, or widget identity bugs. The release
candidate checklist must include:

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

v0.6.0 documents the current keyboard behavior in the README. v1 must keep that
documentation current for the default Textual UI:

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
release. v0.6.0 links users here and asks for structured reports, but does not
claim a finished compatibility matrix. At minimum, v1 should be checked in:

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

Before v1:

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
- Layout is intentionally modest. There are no sidebars, columns API freeze,
  arbitrary browser components, or hosted auth features in the v1 gate.
- API signatures, callback behavior, disabled behavior, generated-key behavior,
  and form submit semantics need final reference docs before v1.

## Remaining v1 Gates

- Finalize the API reference from the stable-candidate table, including
  signatures, return values, callbacks, `args`/`kwargs`, disabled behavior, and
  `key` behavior.
- Capture terminal compatibility evidence for macOS, Linux, SSH/headless or
  container workflows, narrow terminals, and wide terminals.
- Fix or document narrow-rendering issues for tables, charts, forms, expanders,
  and long labels.
- Verify clean installs and example flows from the built wheel/source
  distribution, not only from an editable checkout.
- Run release-candidate checks against the package that will be published.
- Keep changelog, release notes, README, roadmap, and feedback docs aligned.
- Save public launch-style announcement pushes until v1.0.0 is published and
  verified.

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
