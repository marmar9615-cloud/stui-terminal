# Roadmap

`stui` is a small Streamlit-inspired framework for terminal-native Python apps.
This roadmap describes the areas the project is exploring, without promising a
timeline or compatibility with Streamlit.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Now

- Keep the core API small, readable, and easy to explain.
- Improve reliability around reruns, widget state, callbacks, and terminal error
  display.
- Land the v0.3.0 terminal app primitives: forms, containers, static
  expanders, metrics, and simple terminal-native bar charts.
- Polish existing examples so new users can quickly understand where `stui`
  fits: local tools, SSH sessions, model/debug panels, and small data scripts.
- Keep packaging, release notes, and public documentation accurate for the
  current feature set.
- Preserve the no-browser boundary: no server runtime, websockets, local ports,
  or Streamlit runtime dependency.

## Next

- Richer dataframe support for browsing, formatting, and inspecting tabular data
  in terminal apps.
- More layout primitives for common app shapes beyond containers and expanders.
- More chart shapes if the initial terminal-native bar chart proves useful.
- Caching and session persistence for expensive local computations and repeated
  workflows.
- Theming hooks for projects that need a consistent visual style.
- Mouse support improvements where Textual already provides useful first-party
  behavior.
- Screenshot and GIF documentation that shows real terminal output and common
  workflows.

## Later

- A plugin or widget extension API for custom components that can live outside
  the core package.
- More complete table interactions, including selection, sorting, and wider
  display-format control.
- Better keyboard navigation patterns for larger apps.
- More complete form semantics if real workflows need them.
- More example apps that reflect real local workflows rather than toy demos.
- Developer tooling that makes it easier to inspect app state, reruns, and
  widget identity while building.

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
- Whether v0.3.0 forms, containers, expanders, metrics, or charts are expressive
  enough for a real terminal app.
- Whether the terminal UI behaved well with your shell, font, theme, and
  terminal emulator.
- Where keyboard or mouse behavior made the app feel slower than a script or a
  browser dashboard.
- Which examples or docs would have made the first run clearer.
