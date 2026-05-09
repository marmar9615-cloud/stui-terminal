# Release Checklist

Use this checklist for public releases of `stui-terminal`, the PyPI
distribution that provides the `stui` import package and `stui` command.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Decide Release Type

- Patch: bugs, docs, examples, tests, packaging, or project metadata.
- Minor: new public APIs, new widgets, or meaningful behavior additions.
- Breaking: do not ship before 1.0 unless a severe correctness or safety issue
  requires it.

If a change adds API surface, it is not a patch release.

## Pre-Release Triage

- Review open bug reports and recent discussions on Monday or Tuesday when
  possible.
- Confirm any release-blocking issue has a reproducible case.
- Move broad feature ideas into feedback collection instead of rushing them into
  the release.
- Check docs for honest scope: terminal-native, Streamlit-inspired, not
  Streamlit-compatible, no browser/server/runtime Streamlit dependency.

## Local Verification

Run from the repository root:

```bash
python3.11 -m pytest
git diff --check
```

For package publishing, also follow `docs/publishing.md` and run the build and
twine checks listed there.

## Public Copy

Before publishing release notes, confirm they do not imply:

- Official Streamlit affiliation.
- Streamlit compatibility.
- Browser, server, websocket, or port-forwarding support.
- Production maturity beyond the current tested surface.
- Widget or layout coverage that does not exist yet.

## Release Window

- Monday and Tuesday are best for triage and final release decision-making.
- Midweek is best for small bug, docs, example, and metadata fixes.
- Friday and the weekend should be patch-only, and only when a real fix needs to
  reach users.

## After Release

Pause feature churn for several days after this release.

During the pause:

- Let users try the package in real terminal environments.
- Collect terminal feedback: rendering, keyboard behavior, SSH/container quirks,
  and color/readability issues.
- Collect API feedback: whether the current widget, callback, rerun, and
  `session_state` model feels simple enough.
- Patch reproducible bugs or docs/package metadata mistakes.
- Defer large features until enough feedback shows the next API direction.
