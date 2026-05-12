# Feedback

Thanks for trying `stui`. The project is intentionally small, terminal-native,
and Streamlit-inspired without being Streamlit-compatible.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Now

Feedback that is most helpful right now:

- Terminal reports from real shells, SSH sessions, containers, headless
  environments, narrow terminals, wide terminals, unusual fonts, and different
  color themes. Include whether the app was local, over SSH, in a container, or
  inside an editor terminal.
- Keyboard bugs: focus order, `Tab`/`Shift+Tab`, button activation, text or
  number input submission, checkbox toggles, selectbox/radio movement, slider
  keys, expander toggles, and any keys captured by the terminal instead of the
  app.
- Narrow rendering bugs: clipped labels, wrapped buttons, unreadable tables,
  chart output that loses meaning, form layout issues, expander children that
  become hard to scan, and help/footer text that crowds the app.
- Install and package issues: `pip install stui-terminal`, `stui` command not
  found, `python -m stui`, editable installs, bundled examples, `stui example
  copy`, and `stui init`.
- API signature confusion: names, parameter order, return values, callbacks,
  `args`/`kwargs`, stable `key` behavior, disabled widgets, form submit
  semantics, reruns, `st.stop`, and `session_state`.
- Docs or example gaps: unclear README snippets, missing API reference detail,
  examples that only work from a checkout, `stui init` template confusion, or a
  kitchen-sink example that does not match the documented stable-candidate API.
- Desired examples: local tools, SSH workflows, data scripts, model/debug
  panels, DevOps dashboards, forms, charts, layouts, narrow terminal examples,
  and kitchen-sink coverage.
- Places where README, release notes, or examples make a feature look broader
  than it really is.
- Bugs that can be reproduced with a short `stui run` script.

## Next

Feedback that can shape near-term design:

- Charts: whether the first bar chart helper is enough, and which chart
  types are useful in a terminal without color.
- Richer dataframe support: which table interactions matter first for
  inspection and debugging.
- Layout primitives: what should come after containers and expanders.
- Forms: where submit-style flows feel natural or surprising in a top-to-bottom
  rerun model.
- Caching and session persistence: what data should persist, for how long, and
  how explicit that behavior should be.
- Theming: which parts of the terminal UI need project-level styling control.
- Mouse support improvements: where mouse behavior should complement keyboard
  control without becoming required.
- Screenshot and GIF docs: which workflows would be clearer with recorded
  terminal examples.

## Later

Feedback that is useful but may require more design work:

- Plugin or widget extension API needs for project-specific components.
- Advanced table behavior such as sorting, selection, and formatting.
- Navigation patterns for larger multi-section terminal apps.
- Debugging tools for reruns, widget identity, state changes, and layout.
- Example apps that would prove `stui` works for real local workflows.

## Not Planned Yet

These are not current project goals:

- Streamlit compatibility mode.
- Browser, server, websocket, or port-forwarding support.
- Runtime dependency on Streamlit.
- Full Streamlit forms, layout, or chart compatibility.
- A large component ecosystem inside the core package before the MVP settles.
- GPL slider/widget code or dependencies with licensing concerns.
- Hosted cloud features, managed auth, or deployment infrastructure.

## What To Include

When opening an issue or sending feedback, include:

- Your operating system, terminal emulator, shell, and Python version.
- The `stui` version and install method.
- The output of `stui doctor`.
- `TERM`, `COLORTERM`, `TERM_PROGRAM`, and terminal size if rendering or
  keyboard behavior is involved.
- A minimal script that reproduces the issue or demonstrates the missing
  workflow.
- What you expected to happen and what happened instead.
- Whether the app was local, over SSH, in a container, or in another constrained
  environment.

Public announcement-style pushes are intentionally saved for v1.0.0. Pre-1.0
feedback should focus on whether the package is clear, installable, usable in
real terminals, and small enough to stabilize.
