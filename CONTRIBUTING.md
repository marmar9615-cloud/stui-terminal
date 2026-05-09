# Contributing

Thanks for helping with `stui`. The project is still an MVP, so the best
contributions keep the surface area small, readable, and easy to test.

## Local Setup

Use Python 3.11 or newer:

```bash
python3.11 -m pip install -e ".[dev]"
python3.11 -m pytest
```

## Development Guidelines

- Keep the public API small and Streamlit-inspired, not Streamlit-compatible.
- Do not add browser, server, websocket, or port-forwarding code.
- Do not depend on Streamlit at runtime.
- Prefer Textual first-party widgets where they exist.
- Do not copy GPL slider code or depend on packages such as `textual-slider`.
- Keep MVP code direct before adding abstractions.
- Keep examples local and deterministic; avoid network calls unless the project
  explicitly grows that capability later.

## Tests

Run the full test suite after code changes:

```bash
python3.11 -m pytest
```

Documentation-only edits should still be checked for accuracy against the
current API and examples.

## Public Claims

Please keep README and release notes honest:

- Say `stui` is inspired by Streamlit, not compatible with it.
- Say `stui` is not official Streamlit and is not affiliated with Streamlit.
- Avoid implying production hardening, broad widget coverage, browser support,
  or long-term API stability before those things exist.
