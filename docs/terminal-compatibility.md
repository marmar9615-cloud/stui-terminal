# Terminal Compatibility

`stui` is terminal-native and built on Textual/Rich. It does not open a browser,
bind a port, run a dashboard server, use websockets, or depend on Streamlit at
runtime.

Terminal support is intentionally reported from evidence. If a terminal is
listed as unknown or test-needed, that means the project has not verified it
well enough to promise support.

## Compatibility Matrix

| Environment | Status | Notes |
| --- | --- | --- |
| macOS Terminal.app | Expected to work; local smoke-needed before claiming fully supported | Textual/Rich generally render in Terminal.app. Please report font, color, mouse, or resize issues with `stui doctor` output. |
| iTerm2 | Expected to work; local smoke-needed before claiming fully supported | Likely a good local macOS target, especially with 256-color or truecolor enabled. Not enough project-owned evidence yet for a stronger claim. |
| VS Code integrated terminal | Expected to work; local smoke-needed before claiming fully supported | Common development target. Behavior can vary by shell, font, theme, and remote/container mode. |
| Warp | Unknown/test-needed | Modern terminal behavior may differ from classic PTY assumptions. Please report any keyboard, focus, or redraw issues. |
| SSH/headless sessions | Supported goal; test-needed by host terminal | This is a core use case, but behavior depends on the client terminal, remote `$TERM`, locale, and available terminal size. |
| Codespaces/devcontainers | Unknown/test-needed | Expected to depend on the web terminal or local editor terminal front end. Not verified enough to claim support. |
| Linux terminals | Unknown/test-needed | Please include distro, terminal emulator, `$TERM`, `$COLORTERM`, and whether the app runs locally, over SSH, or in a container. |
| Windows Terminal | Unknown/test-needed | Not verified by the project yet. Reports from PowerShell, WSL, and native Python installs are useful, but should be labeled with the exact setup. |
| Very small terminals below 80x24 | Known constrained mode | `stui doctor` warns when the active terminal is below 80 columns or 24 rows. Apps may still start, but layouts, tables, and charts can clip. |
| `TERM=dumb` or missing color env | Diagnostic-only coverage | `stui doctor` reports the environment as limited. The project does not yet claim a graceful degraded UI for every dumb-terminal path. |

## Minimum Terminal Shape

Use at least an 80x24 terminal when possible. Smaller terminals may still launch,
but layouts and charts can clip or become hard to read.

Run:

```bash
stui doctor
```

For machine-readable bug reports or CI artifacts, run:

```bash
stui doctor --json
```

The doctor output includes:

- `stui`, package, Python, Textual, Rich, and Typer versions.
- Terminal size and a warning when it is below the recommended minimum.
- Resolved theme.
- `TERM`, `COLORTERM`, `TERM_PROGRAM`, `STUI_THEME`, and `NO_COLOR`.
- Whether standard input, output, and error streams are attached to a TTY.
- A best-effort color capability summary.
- Installed example availability.

`STUI_THEME=high-contrast` enables the high-contrast theme. Any other value
falls back to the default theme and should be included in reports if the theme
does not look right. `NO_COLOR` is reported by `stui doctor` so users can spot
color-related environment differences; do not assume every terminal front end
handles it the same way.

Current automated coverage checks the doctor output, `stui doctor --json`, color
capability classification for `TERM`/`COLORTERM`, `STUI_THEME` resolution, and
small-terminal warnings. It does not replace manual visual checks in real
terminal emulators.

## Reporting Compatibility Bugs

When opening a terminal compatibility issue, include:

- The exact command you ran, such as `stui run app.py` or `python -m stui run app.py`.
- Full `stui doctor` output.
- Operating system and version.
- Terminal emulator and version.
- Shell, for example `zsh`, `bash`, `fish`, PowerShell, or WSL shell.
- Whether the run was local, over SSH, inside a container/devcontainer, in
  Codespaces, or in another constrained environment.
- Terminal size when the issue happened.
- A minimal `stui` script that reproduces the behavior.
- What you expected and what happened instead.
- A screenshot or short terminal recording if the issue is visual.

Please do not report `stui` as a Streamlit compatibility issue. `stui` is
Streamlit-inspired, but it is not official Streamlit, is not affiliated with
Streamlit, and is not a Streamlit compatibility layer.
