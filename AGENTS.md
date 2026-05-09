# stui Agent Notes

- Always run `python3.11 -m pytest` after code changes.
- Keep the public API small and Streamlit-inspired, not Streamlit-compatible.
- Do not add browser, server, websocket, or port-forwarding code.
- Do not depend on Streamlit at runtime.
- Do not copy GPL slider code or depend on packages such as `textual-slider`.
- Prefer Textual first-party widgets where they exist.
- Keep the MVP implementation readable and direct before adding abstractions.
- Keep public docs honest: `stui` is not official Streamlit, not affiliated with Streamlit, and not a Streamlit compatibility layer.
- When working alongside other agents, do not revert edits you did not make.
