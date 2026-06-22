# Release Checklist

Use this checklist for public releases of `stui-terminal`, the PyPI
distribution that provides the `stui` import package and `stui` command.

`stui` is not official Streamlit, is not affiliated with Streamlit, and is not a
Streamlit compatibility layer.

## Decide Release Type

- Patch: bugs, docs, examples, tests, packaging, or project metadata.
- Minor: new public APIs, new widgets, or meaningful behavior additions.
- Breaking: reserve for a future major release unless a severe correctness or
  safety issue requires an immediate documented tightening.

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
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
stui --version
python -m stui --version
./scripts/check.sh
git diff --check
```

For package publishing, also follow `docs/publishing.md`.

## Installed-Package Verification

Before publishing, verify the current public package still installs cleanly:

```bash
python3.11 -m venv /tmp/stui-current
/tmp/stui-current/bin/python -m pip install --upgrade pip
/tmp/stui-current/bin/python -m pip install --index-url https://pypi.org/simple --no-cache-dir stui-terminal
/tmp/stui-current/bin/python -c "import stui; print(stui.__version__)"
/tmp/stui-current/bin/stui --version
/tmp/stui-current/bin/stui doctor --json
/tmp/stui-current/bin/stui examples
/tmp/stui-current/bin/stui example list
/tmp/stui-current/bin/stui example copy basic /tmp/stui-basic.py
/tmp/stui-current/bin/stui init /tmp/stui-app.py
/tmp/stui-current/bin/stui init /tmp/stui-data-app.py --template data
/tmp/stui-current/bin/stui init /tmp/stui-charts-app.py --template charts
/tmp/stui-current/bin/stui check /tmp/stui-app.py --strict
/tmp/stui-current/bin/stui selftest --strict
```

After publishing, repeat the same check with the exact released version, for
example `stui-terminal==X.Y.Z`.

## Tag, CI, Publish, Release

1. Commit only after local verification is green.
2. Create and push the release tag, for example `vX.Y.Z`.
3. Wait for CI on `main` and the tag.
4. Dispatch the `Publish` workflow from the release tag with exactly one publish
   flag enabled.
5. Approve the protected PyPI environment only after CI, build, Twine, security,
   and fresh-wheel checks are green.
6. Confirm PyPI JSON and the Simple API show the new release.
7. Verify a clean install from PyPI with the exact version.
8. Create the GitHub Release from the matching
   `docs/releases/RELEASE_NOTES_*.md` file.

## Final v1.0.0 Flow

Use this stricter flow for the stable v1 launch:

1. Freeze code and docs together: version metadata, README, API reference, API
   stability table, changelog, release notes, v1 readiness, feedback docs,
   and roadmap must describe the same shipped surface.
2. Run local gates from a clean checkout or refreshed virtual environment:
   `ruff check .`, `python3.11 -m pytest`, `python -m build`,
   `python -m twine check dist/*`, `./scripts/check.sh`, and
   `git diff --check`.
3. Inspect built artifacts for README/assets/examples/release-note inclusion
   before creating the tag.
4. Smoke the built wheel in a temporary virtual environment: import `stui`, run
   version/doctor commands, list/copy examples, list demos, launch one demo when
   practical, create each documented template, and run at least one copied
   example with `python -m stui run`.
5. Refresh `docs/terminal-compatibility.md` with the evidence actually gathered
   for v1.0.0 and keep unverified environments marked test-needed.
6. Confirm the README/PyPI screenshot URL renders and represents a real
   terminal app from the shipped code.
7. Tag `v1.0.0` only after the release diff is final and no other agent has
   unreviewed edits in the owned docs.
8. Wait for `main` and tag CI, then publish from the tag through Trusted
   Publishing with only the real PyPI flag enabled.
9. Verify PyPI JSON, the Simple API, and a clean exact-version install from
   PyPI.
10. Create the GitHub Release from the matching v1.0.0 release notes in
    `docs/releases/`.
11. Publish X, LinkedIn, and GitHub Discussion launch copy only after the exact
   PyPI release, docs, screenshot, examples, and CI are verified.

## Routine v1.x Flow

Use this flow for v1.1.0 and later v1.x maintenance/minor releases:

1. Freeze code and docs together: version metadata, README, API reference, API
   stability table, changelog, release notes, v1 readiness, feedback docs, and
   roadmap must describe the same shipped surface.
2. Run local gates from a clean checkout or refreshed virtual environment:
   `ruff check .`, `python3.11 -m pytest`, `python -m build`,
   `python -m twine check dist/*`, `./scripts/check.sh`, and
   `git diff --check`.
3. Inspect built artifacts for README/assets/examples/release-note inclusion
   before creating the tag.
4. Run `python scripts/check_release_version.py --tag vX.Y.Z` before pushing
   the tag so `pyproject.toml`, `stui.__version__`, and the Git tag agree.
5. Smoke the built wheel in a temporary virtual environment: import `stui`, run
   version/doctor commands, list/copy examples, list demos, create each
   documented template including `data` and `charts`, run
   `stui check --strict --repeat 2` on copied or initialized apps, run
   `stui selftest --strict --repeat 2`, and run at least one copied example with
   `python -m stui run` when practical.
6. Run at least one repeated-run/recovery gate before tagging: `stui check` with
   `--repeat`, a strict selftest with `--repeat`, and the runtime regression
   tests that cover rerun exhaustion, form pending state, and authoring-error
   rollback.
7. Tag only after the release diff is final and no helper has unreviewed edits.
8. Wait for `main` and tag CI, then publish from the tag through Trusted
   Publishing with only the real PyPI flag enabled.
9. Verify PyPI JSON, the Simple API, and a clean exact-version install from
   PyPI.
10. Create the GitHub Release from the matching release notes in
   `docs/releases/`.
11. Do not generate X, LinkedIn, X thread, or GitHub Discussion copy unless a
   separate task explicitly asks for it.

## v2 Major Release Prep

Use this extra gate for v1.9.0 and v2.0.0:

1. Update `docs/v2-readiness.md` with the stable API contract, experimental
   APIs, deferred roadmap, migration expectations, and release-proof checklist.
2. Confirm the stable and experimental API lists in `docs/v2-readiness.md`
   match `docs/api-stability.md`, `docs/api-reference.md`, README, and public
   API tests.
3. Keep broad post-v2 work deferred unless a small bug fix is necessary for the
   v2 contract.
4. Verify current PyPI stable before publishing the major release.
5. Run clean wheel install, exhaustive CLI checks, package audit, repo hygiene
   audit, and custom external project validation before tagging and publishing.
6. Do not say v2 is shipped until PyPI, GitHub tag/release, CI, fresh install,
   CLI checks, package contents audit, repo hygiene audit, and custom project
   validation are all verified.

## v1 Release Gates

Before tagging v1.x releases, confirm:

- Version metadata, README, `CHANGELOG.md`, `docs/releases/` release notes, and
  readiness docs all name the same release.
- `scripts/check_release_version.py --tag vX.Y.Z` passes for the intended tag.
- Stable and experimental API labels agree across README,
  `docs/api-reference.md`, `docs/api-stability.md`, and public API tests.
- `stui-terminal` remains the PyPI distribution name; `stui` remains the import
  package and CLI command.
- The public docs preserve the non-affiliation and non-compatibility language:
  not official Streamlit, not affiliated with Streamlit, and not a Streamlit
  compatibility layer.
- No browser, server, websocket, port-forwarding, Streamlit runtime, GPL slider
  code, or `textual-slider` dependency has been introduced.
- Installed-package flows work without a repository checkout: `stui examples`,
  `stui demo list`, `stui demo NAME`, `stui example list`,
  `stui example copy`, `stui init`, `stui check --strict --repeat 2`, and
  `stui selftest --strict --repeat 2`.
- v1.2.0 and later minor releases run `scripts/verify_custom_project.sh` from
  outside the repository or through `./scripts/check.sh` to prove a multi-file
  external project can import helpers and validate with `stui check`.
- v1.3.0 and later minor releases run
  `scripts/audit_package_contents.py dist --version X.Y.Z` after building to
  prove wheel/sdist contents are intentional and version-matched.
- Terminal compatibility evidence or explicit test-needed labels are current in
  `docs/terminal-compatibility.md`.
- Public launch-style announcement copy is not generated for routine v1.x
  releases unless explicitly requested.

For v1.0.0 specifically, also confirm the final checklist in
[`docs/v1-readiness.md`](v1-readiness.md#final-v10-checklist).

For v1.9.0 and v2.0.0, also confirm the final checklist in
[`docs/v2-readiness.md`](v2-readiness.md#final-v2-checklist).

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
