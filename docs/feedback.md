# Feedback

Thanks for trying `stui`. The project is intentionally small, terminal-native,
and Streamlit-inspired without being Streamlit-compatible.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## For v1 Users

Feedback that is most helpful right now:

- First-run reports from clean installs: `python -m pip install stui-terminal`,
  `stui --version`, `python -m stui --version`, `stui doctor`, `stui example
  copy`, `stui init`, and `stui run`.
- Whether the PyPI landing page and README made the package/import/CLI split
  clear: install `stui-terminal`, import `stui`, run `stui`.
- Whether the quickstart and first app worked without cloning the repository.
- Whether the screenshot and examples accurately set expectations for a
  terminal-native app instead of a browser dashboard.
- Stable versus experimental API labels: places where README,
  `docs/api-stability.md`, `docs/api-reference.md`, or examples disagree about
  whether an API is `v1-stable` or `pre-v1 experimental`.
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
  copy`, `stui init`, and the `basic`, `dashboard`, or `forms` templates.
- API signature confusion: names, parameter order, return values, callbacks,
  `args`/`kwargs`, stable `key` behavior, disabled widgets, form submit
  semantics, reruns, `st.stop`, and `session_state`.
- API contract mismatches: anything in `docs/api-reference.md` that does not
  match what the package actually does, especially after installing from PyPI
  instead of running from a checkout.
- Docs or example gaps: unclear README snippets, missing API reference detail,
  examples that only work from a checkout, `stui init` template confusion, or a
  kitchen-sink example that does not match the documented stable API.
- Example packaging issues: bundled examples missing from an installed package,
  `stui example copy` writing confusing starter code, or `stui init` templates
  that do not run with `python -m stui run`.
- Desired examples: local tools, SSH workflows, data scripts, model/debug
  panels, DevOps dashboards, forms, charts, layouts, narrow terminal examples,
  and kitchen-sink coverage.
- Places where README, release notes, or examples make a feature look broader
  than it really is.
- Limitations or non-goals that are still unclear, especially around Streamlit
  compatibility, browser/server behavior, hosted/cloud scope, dataframe
  behavior, plotting behavior, layout, tabs, sidebars, or GPL widget code.
- Bugs that can be reproduced with a short `stui run` script.

## v1.1 Feedback

Feedback that can shape near-term design:

- Terminal evidence: which environments should move from unknown/test-needed to
  supported before v1.
- Package hardening: whether install, copy, init, and example flows work from
  clean virtual environments and built artifacts.
- Charts: whether the first bar chart helper is enough, and which chart
  types are useful in a terminal without color.
- Richer dataframe support: which table interactions matter first for
  inspection and debugging.
- Layout primitives: whether containers, integer-count columns, and expanders
  are enough for v1, and what real workflow would justify ratios, tabs,
  sidebars, or a larger layout system.
- Forms: where submit-style flows feel natural or surprising in a top-to-bottom
  rerun model.
- Caching and session persistence: what data should persist, for how long, and
  how explicit that behavior should be.
- Theming: which parts of the terminal UI need project-level styling control.
- Mouse support improvements: where mouse behavior should complement keyboard
  control without becoming required.
- Screenshot and GIF docs: which workflows would be clearer with recorded
  terminal examples.
- v1.1 candidates: which experimental APIs already feel stable enough, and
  which should stay experimental because their terminal behavior is not clear.

## v1.2 And Later Feedback

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

Public launch copy is prepared for v1.0.0, but social posts should still be
posted manually only after the exact PyPI package and GitHub Release are
verified. Post-v1 feedback should focus on whether the stable surface is clear,
installable, usable in real terminals, and small enough to maintain.
