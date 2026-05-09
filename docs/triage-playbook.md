# Triage Playbook

Use this playbook to sort incoming issues, discussions, and direct feedback
without expanding the project faster than the API can settle.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Weekly Flow

- Monday and Tuesday: triage new issues and discussions, ask for missing
  reproduction details, and group feedback themes.
- Midweek: fix small bugs, clarify docs, improve examples, and clean package
  metadata.
- Friday and the weekend: patch only if a real bug, docs mistake, or packaging
  issue needs a quick release.

## First Questions

For every report, identify:

- Is this a reproducible bug in an existing API?
- Is this unclear documentation or an example that overpromises?
- Is this package metadata, install, or release workflow cleanup?
- Is this a request for a new API or widget?
- Is this asking for Streamlit compatibility, browser/server behavior, or
  another out-of-scope direction?

## Routing

- Existing API bug: reproduce with a short script, fix narrowly, and consider a
  patch release.
- Docs or examples: correct the claim, keep wording honest, and consider a patch
  release if published docs are misleading.
- Package metadata: fix narrowly and consider a patch release if install or
  discovery is affected.
- New API or widget: collect use cases first; plan for a minor release only when
  the shape is clear.
- Breaking change: defer before 1.0 unless a severe correctness or safety issue
  requires it.
- Out of scope: close or defer with a short explanation that `stui` is
  terminal-native and not a Streamlit compatibility layer.

## Feedback To Collect

Terminal feedback:

- Operating system, terminal emulator, shell, and Python version.
- Local, SSH, container, or headless environment.
- Rendering, keyboard, mouse, color, and sizing behavior.
- A short script or command that shows the issue.

API feedback:

- Which current API was hard to understand or compose.
- Whether reruns, callbacks, widget keys, and `session_state` behaved as
  expected.
- The smallest script that demonstrates the missing workflow.
- Whether the need is a bug fix, docs clarification, or a new public API.

## Post-Release Pause

After this release, avoid feature churn for several days. Keep triage open,
collect real terminal and API feedback, and patch only clear bugs, docs mistakes,
or package metadata problems.

Large features should wait until feedback shows repeated demand and a small,
readable API shape.
