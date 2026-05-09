# stui Announcement Drafts

## Short X Post

I just shipped `stui` v0.1.0rc2: a tiny Streamlit-inspired terminal UI
experiment for Python.

Write a small Python script, run `stui run app.py`, and get a Textual TUI. No
browser, no ports, no local server.

Early MVP, intentionally small. The PyPI package name is `stui-terminal`; the
import stays `stui`.

https://github.com/marmar9615-cloud/stui-terminal

## Longer X Thread

1. I shipped `stui` v0.1.0rc2 today.

It is a tiny Streamlit-inspired terminal UI experiment for Python: write a
small script, run it from the shell, and get an interactive TUI.

No browser. No ports. No local web server.

https://github.com/marmar9615-cloud/stui-terminal

2. The idea is not to replace Streamlit.

It is for the moments where a browser dashboard feels like too much ceremony:
SSH sessions, headless boxes, local model/debug panels, quick internal tools,
and prototypes that already live in the terminal.

3. The current API is deliberately small:

`title`, `write`, `button`, `slider`, `text_input`, `checkbox`, alerts, and
`session_state`.

Scripts rerun top-to-bottom when widgets change, with state preserved between
runs.

4. It is built with Textual and Rich, packaged as a normal Python project, and
has a small pytest suite plus GitHub Actions CI.

This is an early RC, so there are plenty of limitations: no charts, dataframes,
sidebar, columns, forms, caching, or file upload yet.

The PyPI distribution is `stui-terminal`; the import package and CLI remain
`stui`.

5. I wanted a clean-room, terminal-native Python UI layer that feels familiar
without pretending to be full Streamlit compatibility.

If that sounds useful for your local tools or model prototypes, the repo is
here:

https://github.com/marmar9615-cloud/stui-terminal

## LinkedIn Post

I shipped `stui` v0.1.0rc2, a tiny Streamlit-inspired
terminal UI experiment for Python.

The goal is simple: let you write small Python apps with a familiar
top-to-bottom scripting model, but render them directly in the terminal as a
Textual TUI.

No browser. No port forwarding. No local web server.

This is meant for the places where a browser dashboard is more ceremony than
help: SSH sessions, headless machines, quick internal tools, model/debug panels,
and prototypes that already start in a shell.

The current MVP includes:

- `st.title`, `st.write`, `st.header`, `st.markdown`, `st.text`
- `st.button`, `st.slider`, `st.text_input`, `st.checkbox`
- `st.session_state`
- alert boxes, dividers, reruns, and terminal traceback panels
- examples and GitHub Actions CI

The PyPI distribution is `stui-terminal`, while the Python import and CLI stay
`stui`.

It is intentionally not official Streamlit, not affiliated with Streamlit, and
not a compatibility layer. It is a small clean-room experiment inspired by the
mental model.

There is still a lot missing: charts, dataframes, columns, sidebar, forms,
caching, and file upload are not part of this RC.

Repo:
https://github.com/marmar9615-cloud/stui-terminal
