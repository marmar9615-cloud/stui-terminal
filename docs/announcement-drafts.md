# stui Announcement Drafts

Use these drafts for the stable `stui-terminal` v0.2.0 public launch.

## Short X Post

`stui` v0.2.0 is live from MarMar Labs.

It is a tiny Streamlit-inspired framework for Python apps that render directly in the terminal with Textual.

No browser. No ports. No Streamlit dependency.

Install:

```bash
python -m pip install stui-terminal
```

I would love feedback from builders who live in terminals.

https://github.com/marmar9615-cloud/stui-terminal

## X Thread

1. `stui` v0.2.0 is live from MarMar Labs.

It is a tiny Streamlit-inspired Python UI framework that renders as a Textual app directly in your terminal.

No browser. No ports. No local web server. No Streamlit dependency.

https://github.com/marmar9615-cloud/stui-terminal

2. The package name on PyPI is `stui-terminal`, while the import package and CLI stay `stui`:

```bash
python -m pip install stui-terminal
stui run app.py
```

```python
import stui as st
```

3. The current stable API covers the basics for small terminal apps:

text, markdown, alerts, buttons, sliders, text input, checkboxes, number inputs, selectboxes, radio groups, progress, JSON/code output, simple tables, `session_state`, and reruns.

4. The goal is not Streamlit compatibility.

The goal is a small clean-room terminal-native layer for local tools, SSH sessions, model/debug panels, demos, and scripts where a browser dashboard is extra ceremony.

5. Still intentionally small: no charts, columns, sidebar, forms, caching, file upload, or full dataframe editing yet.

That is the point of this launch: get real feedback before overbuilding.

6. Feedback I would love:

- what terminal-first use case would you try first?
- which widget or display primitive is missing first?
- does the rerun/state model feel natural in a TUI?
- where do the docs/examples get confusing?

Repo:
https://github.com/marmar9615-cloud/stui-terminal

## LinkedIn Post

I shipped `stui` v0.2.0 from MarMar Labs.

`stui` is a tiny Streamlit-inspired Python UI framework for building terminal apps with a familiar top-to-bottom scripting model.

No browser. No port forwarding. No local web server. No Streamlit dependency.

The goal is not to replace Streamlit. It is for the places where a browser dashboard feels like more ceremony than help: SSH sessions, headless machines, quick internal tools, model/debug panels, and prototypes that already start in a shell.

The current stable release includes:

- text, markdown, code, JSON, progress, alerts, and traceback display
- buttons, sliders, text input, checkboxes, number inputs, selectboxes, and radio groups
- simple static tables without requiring pandas
- `st.session_state` and script reruns
- `stui doctor`, `stui examples`, examples, tests, CI, and PyPI publishing

The PyPI distribution is `stui-terminal`, while the Python import and CLI stay `stui`.

```bash
python -m pip install stui-terminal
```

This is intentionally not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer. It is a clean-room, terminal-native project inspired by the scripting model.

There is still a lot missing: charts, dataframe editing, columns, sidebar, forms, caching, and file upload are not part of the stable 0.2 API.

I am excited about the shape of it, but I want to keep the promise honest: small API, readable implementation, and enough working surface to test whether the idea is useful.

I would love feedback from people building local tools, AI/model workflows, internal CLIs, and terminal-first prototypes.

Repo:
https://github.com/marmar9615-cloud/stui-terminal

## GitHub Discussion / Feedback Post

Title: `stui` v0.2.0 feedback thread

I shipped `stui` v0.2.0 from MarMar Labs and would love feedback from builders who might use a small Python UI framework directly in the terminal.

`stui` is Streamlit-inspired, but it is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer. The goal is a clean-room, terminal-native API for small local apps, SSH-friendly tools, model/debug panels, and prototypes that do not need a browser.

Current shape:

- install from PyPI as `stui-terminal`
- import and CLI stay `stui`
- run apps with `stui run app.py`
- render with Textual and Rich
- use a compact API for text, status, inputs, progress, tables, reruns, and `session_state`

This is an honest early stable release. It has examples, tests, CI, and packaging, but there is plenty missing: charts, dataframe editing, columns, sidebar, forms, caching, file upload, and broader widget coverage.

Feedback I would especially appreciate:

- What terminal-first use case would you try first?
- Which widget or display primitive should come next?
- Does the rerun/state model feel natural in a TUI?
- Is the install/import naming clear enough with `stui-terminal` on PyPI and `stui` for the CLI/import?
- What should stay out of scope so the project remains small and readable?
