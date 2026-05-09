# Security Policy

## Supported Versions

`stui` is an early project. Security fixes are expected to target the current
released version and the main development branch unless the maintainers state a
different policy in a future release.

## Reporting a Vulnerability

Please do not publish sensitive vulnerability details in a public issue.

Use GitHub private vulnerability reporting for this repository. If that path is
temporarily unavailable, open a minimal public issue asking for a private
contact path and avoid including exploit details, secrets, or private system
information.

Helpful reports include:

- Affected `stui` version or commit.
- Python version, operating system, and terminal environment.
- A minimal reproduction, when it is safe to share.
- Expected impact and any known workaround.

## Project Boundary

`stui` is a local, terminal-native Python package. It should not start a browser
runtime, bind a web server, use websockets, or require port-forwarding. Security
reports about those behaviors are still useful if they show the boundary has
been accidentally crossed.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.
