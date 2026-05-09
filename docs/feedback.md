# Feedback

Thanks for trying `stui`. The project is intentionally small, terminal-native,
and Streamlit-inspired without being Streamlit-compatible.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Now

Feedback that is most helpful right now:

- Reports about existing widgets, reruns, callbacks, and `session_state`.
- Terminal rendering issues in real shells, SSH sessions, and headless
  environments.
- Places where the current examples or README made a feature look broader than
  it really is.
- Small API naming or behavior issues that make simple scripts harder to read.
- Bugs that can be reproduced with a short `stui run` script.

## Next

Feedback that can shape near-term design:

- Charts: which chart types are useful in a terminal, and what output should
  remain readable without color.
- Richer dataframe support: which table interactions matter first for
  inspection and debugging.
- Layout primitives: which app layouts you need before reaching for a browser
  dashboard.
- Forms: how submit-style flows should work in a top-to-bottom rerun model.
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
- A large component ecosystem inside the core package before the MVP settles.
- GPL slider/widget code or dependencies with licensing concerns.
- Hosted cloud features, managed auth, or deployment infrastructure.

## What To Include

When opening an issue or sending feedback, include:

- Your operating system, terminal emulator, shell, and Python version.
- The `stui` version and install method.
- A minimal script that reproduces the issue or demonstrates the missing
  workflow.
- What you expected to happen and what happened instead.
- Whether the app was local, over SSH, in a container, or in another constrained
  environment.
