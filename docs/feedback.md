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
  whether an API is `v1-stable` or `post-v1 experimental`.
- Terminal reports from real shells, SSH sessions, containers, headless
  environments, narrow terminals, wide terminals, unusual fonts, and different
  color themes. Include whether the app was local, over SSH, in a container, or
  inside an editor terminal, plus `stui doctor --compat` when possible.
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

## v1.x Feedback

Feedback that can shape near-term design:

- Terminal evidence: which environments should move from unknown/test-needed to
  supported during the v1 series.
- Package hardening: whether install, copy, init, selftest, and example flows
  work from clean virtual environments and built artifacts.
- `stui check --strict`: whether non-interactive validation catches useful
  script errors and authoring warnings in local or CI workflows.
- Charts: whether the stable bar and line summaries cover real terminal
  dashboard needs, and which future chart types are useful without heavy
  plotting dependencies.
- Richer dataframe support: which table interactions matter first for
  inspection and debugging after `max_rows` and `max_cols`. For table reports,
  include terminal width/height, approximate row and column counts, data shape
  such as list-of-dicts or dict-of-lists, and whether `max_rows` or `max_cols`
  was used.
- Layout primitives: whether containers, integer-count columns, and expanders
  are enough for real terminal apps, and what real workflow would justify
  ratios, tabs, sidebars, or a larger layout system. For layout reports, include
  whether columns stacked earlier or later than expected and whether the layout
  was nested inside another column.
- Forms: where submit-style flows feel natural or surprising in a top-to-bottom
  rerun model.
- Caching and session persistence: what data should persist, for how long, and
  how explicit that behavior should be.
- Theming: which parts of the terminal UI need project-level styling control.
- Mouse support improvements: where mouse behavior should complement keyboard
  control without becoming required.
- Screenshot and GIF docs: whether the current real terminal screenshot and
  `stui demo model_demo` command set expectations clearly.
- Remaining experimental APIs: whether status/spinner or help should graduate,
  stay experimental, or be redesigned.

## Later v1.x Feedback

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
- The output of `stui doctor --compat` for terminal compatibility reports.
- `TERM`, `COLORTERM`, `TERM_PROGRAM`, and terminal size if rendering or
  keyboard behavior is involved.
- A minimal script that reproduces the issue or demonstrates the missing
  workflow.
- What you expected to happen and what happened instead.
- Whether the app was local, over SSH, in a container, or in another constrained
  environment.

Post-v1 feedback should focus on whether the stable surface is clear,
installable, usable in real terminals, and small enough to maintain.
