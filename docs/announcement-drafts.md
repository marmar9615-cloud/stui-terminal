# stui Announcement Drafts

Final launch copy for the `stui-terminal` v0.2.1 public release.

## Final X Post

I shipped `stui` v0.2.1 from MarMar Labs.

It is a small Streamlit-inspired Python UI framework that runs terminal-native apps with Textual.

No browser. No ports. No local web server. No Streamlit runtime dependency.

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

This is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer. It is a clean-room project for builders who want simple Python apps that stay in the terminal.

Feedback welcome.

https://github.com/marmar9615-cloud/stui-terminal

## X Thread

1. I shipped `stui` v0.2.1 from MarMar Labs.

It is a small Streamlit-inspired Python UI framework for terminal-native apps, built on Textual.

No browser. No ports. No local web server. No Streamlit runtime dependency.

https://github.com/marmar9615-cloud/stui-terminal

2. Install from PyPI as `stui-terminal`:

```bash
python -m pip install stui-terminal
```

The import package and CLI stay short:

```python
import stui as st
```

```bash
stui run app.py
```

3. The goal is not Streamlit compatibility.

The goal is a small clean-room API for terminal-first tools: SSH sessions, headless boxes, local model/debug panels, internal utilities, and quick demos where opening a browser is extra ceremony.

4. The current API covers the useful basics:

text, markdown, code, JSON, alerts, buttons, sliders, text input, checkboxes, number inputs, selectboxes, radio groups, progress, simple tables, `session_state`, and reruns.

5. It is intentionally still small.

No charting system, dataframe editor, columns, sidebar, forms, caching, or file upload in the stable API yet.

I would rather learn from real terminal workflows before making the surface area huge.

6. A few things I care about keeping honest:

`stui` is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer.

It does not depend on Streamlit at runtime.

It does not start a browser, web server, or port.

7. Feedback I would genuinely love:

- What would you build with a terminal-native Python app framework?
- Which widget or display primitive is missing first?
- Does the rerun/state model feel natural in a TUI?
- Is the PyPI name `stui-terminal` clear enough?

Repo:
https://github.com/marmar9615-cloud/stui-terminal

## LinkedIn Post

I shipped `stui` v0.2.1 from MarMar Labs.

`stui` is a small Streamlit-inspired Python UI framework for building terminal-native apps with Textual.

The basic workflow is meant to feel direct:

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

No browser. No ports. No local web server. No Streamlit runtime dependency.

The use case is not "replace Streamlit." It is for the moments where a browser dashboard is more ceremony than help: SSH sessions, headless machines, local model/debug panels, internal tools, terminal-first demos, and scripts that already start in a shell.

The current release includes a practical first surface:

- text, markdown, code, JSON, progress, alerts, and traceback display
- buttons, sliders, text input, checkboxes, number inputs, selectboxes, and radio groups
- simple static tables without requiring pandas
- `st.session_state` and script reruns
- examples, tests, CI, CLI helpers, and PyPI packaging

Important boundary: this is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer. It is a clean-room, terminal-native project inspired by the top-to-bottom scripting model.

It is also intentionally small. Charts, dataframe editing, columns, sidebar, forms, caching, file upload, and broader layout primitives are not part of the stable API yet.

I am excited about the shape of it, but I want the next steps to come from real use instead of guesses. If you build local tools, AI/model workflows, internal CLIs, or terminal-first prototypes, I would love feedback on what feels useful, confusing, or missing.

Repo:
https://github.com/marmar9615-cloud/stui-terminal

## GitHub Discussion Feedback Post

Title: `stui` v0.2.1 feedback thread

I shipped `stui` v0.2.1 from MarMar Labs and would love feedback from builders who might use a small Python UI framework directly in the terminal.

`stui` is Streamlit-inspired, but it is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer. It is a clean-room project for terminal-native apps built with Textual.

Install and run:

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

Project boundaries:

- no browser
- no ports
- no local web server
- no Streamlit runtime dependency
- not a Streamlit compatibility layer

Current shape:

- compact Python API for text, status, inputs, progress, code/JSON output, tables, reruns, and `session_state`
- Textual-powered terminal rendering
- PyPI distribution name: `stui-terminal`
- import package and CLI command: `stui`
- examples, tests, CI, and packaging in place

This is an honest early stable release. There is plenty missing: charts, dataframe editing, columns, sidebar, forms, caching, file upload, and broader widget coverage are not in the stable API yet.

Feedback I would especially appreciate:

- What terminal-first use case would you try first?
- Which widget or display primitive should come next?
- Does the rerun/state model feel natural in a TUI?
- Is the install/import naming clear enough?
- What should stay out of scope so the project stays small and readable?

Repo:
https://github.com/marmar9615-cloud/stui-terminal

## Short Dev-Community Reply Post

I built `stui`, a small Streamlit-inspired Python UI framework for terminal-native apps with Textual.

```bash
python -m pip install stui-terminal
```

```python
import stui as st
```

```bash
stui run app.py
```

No browser, no ports, no Streamlit runtime dependency. Also not official Streamlit, not affiliated with Streamlit, and not a compatibility layer.

I am looking for practical feedback from people who build local tools, SSH/headless workflows, model/debug panels, or terminal-first prototypes.
