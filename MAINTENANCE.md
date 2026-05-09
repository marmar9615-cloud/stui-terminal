# Maintenance

`stui` is a small terminal-native project. Maintenance should keep the package
boring, readable, and honest while the API is still young.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Weekly Cadence

- Monday and Tuesday: triage issues, discussions, and incoming feedback.
- Midweek: handle small bugs, docs corrections, example fixes, and package
  metadata cleanup.
- Friday and the weekend: patch only when needed for a real bug, broken docs, or
  release/package metadata problem.

Avoid filling every quiet day with new feature work. Quiet periods after a
release are useful because they show which problems users actually hit.

## Release Sizing

- Patch releases are for bug fixes, docs corrections, examples, tests, and
  package metadata.
- Minor releases are for new public APIs, new widgets, and meaningful behavior
  additions.
- No breaking changes before 1.0 unless there is a severe correctness or safety
  issue and the migration is documented clearly.
- Large features should wait until feedback shows the current API shape is
  holding up in real terminal workflows.

When in doubt, prefer a patch release with a small fix over a minor release that
changes the public surface too early.

## Post-Release Pause

After this release, avoid feature churn for several days. Let users install it,
try it in real shells, and report how the terminal experience and API feel.

During the pause:

- Collect terminal rendering feedback from macOS, Linux, SSH, containers, and
  common terminal emulators.
- Collect API feedback from short scripts that use widgets, callbacks, reruns,
  and `session_state`.
- Fix obvious regressions quickly when they are reproducible.
- Defer large widgets, layout systems, compatibility ideas, and extension APIs
  until feedback points to a clear need.

The goal is to learn from usage, not to make the package look larger than it is.

## Maintenance Boundaries

- Keep the public API small and Streamlit-inspired, not Streamlit-compatible.
- Do not add browser, server, websocket, or port-forwarding code.
- Do not depend on Streamlit at runtime.
- Prefer Textual first-party widgets where they exist.
- Do not copy GPL slider code or depend on packages such as `textual-slider`.
- Keep MVP implementation direct before adding abstractions.
- Keep public docs honest about what exists, what is experimental, and what is
  not planned yet.

## Before Merging Maintenance Changes

- Check that the change is in the right release size: patch for bugs/docs/package
  metadata, minor for new APIs.
- Read the affected docs as a user would read them.
- Run `git diff --check`.
- Run `python3.11 -m pytest` after code changes.
- For docs-only changes, prefer no-code checks such as `git diff --check` and
  targeted searches for stale claims.
