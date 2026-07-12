# Publishing stui-terminal

This project publishes as `stui-terminal` on PyPI using GitHub Actions Trusted
Publishing. TestPyPI is supported as an optional rehearsal target, but real PyPI
publishing must still be an explicit manual workflow dispatch.

The distribution name is `stui-terminal`, while the import package and console
command remain `stui`.

Do not give passwords, API tokens, recovery codes, or `.pypirc` contents to
Codex. If browser help is needed, log in manually first, then Codex can navigate
the already-authenticated browser with Safari or Computer Use.

## Trusted Publisher Setup

Configure Trusted Publishing manually before running the publish workflow.

### 1. Create or Log Into TestPyPI

Open https://test.pypi.org/ and create or log into your TestPyPI account.

### 2. Create or Log Into PyPI

Open https://pypi.org/ and create or log into your PyPI account.

### 3. Configure TestPyPI Trusted Publisher

In TestPyPI, add a pending publisher with:

- Project name: `stui-terminal`
- Owner: `marmar9615-cloud`
- Repository name: `stui-terminal`
- Workflow file name: `publish.yml`
- Environment name: `testpypi`

### 4. Configure PyPI Trusted Publisher

In PyPI, add a pending publisher with:

- Project name: `stui-terminal`
- Owner: `marmar9615-cloud`
- Repository name: `stui-terminal`
- Workflow file name: `publish.yml`
- Environment name: `pypi`

The `pypi` workflow job only runs from an explicit manual dispatch with
`publish_to_pypi=true`.

## Local Verification Before Any Publish

Run these from the repository root:

```bash
RELEASE_TMP="$(mktemp -d "${TMPDIR:-/tmp}/stui-release.XXXXXX")"
trap 'rm -rf "$RELEASE_TMP"' EXIT
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
python3.11 -m pytest
python -m build
python -m twine check dist/*
python scripts/check_release_version.py --tag vX.Y.Z
python scripts/audit_package_contents.py dist --version X.Y.Z
stui --version
python -m stui --version
stui doctor --compat
stui selftest --strict --repeat 2
stui init "$RELEASE_TMP/stui-app.py"
stui check "$RELEASE_TMP/stui-app.py" --strict --repeat 2
STUI_WHEEL=dist/stui_terminal-X.Y.Z-py3-none-any.whl \
  STUI_CUSTOM_PROJECT_DIR="$RELEASE_TMP/custom-project" \
  ./scripts/verify_custom_project.sh
./scripts/check.sh
```

For v2.2.0, also run the release-specific cache/watch/authoring proof against
the built wheel:

```bash
python3.11 -m pytest tests/test_cache.py tests/test_watch_mode.py
python3.11 scripts/verify_v220_project.py \
  --wheel dist/stui_terminal-2.2.0-py3-none-any.whl
```

This validator must operate outside the checkout and prove cache hits,
mutation isolation, resource identity, clearing, TTL/eviction, local helper
reload, session-state preservation, stale-cache invalidation, syntax-error
survival/recovery, and the multiline authoring flow. Do not approve the PyPI
environment if any part is skipped or only inferred from unit tests.

## Trigger TestPyPI Publish

After the TestPyPI Trusted Publisher is configured:

1. Go to GitHub Actions for this repository.
2. Select the `Publish` workflow.
3. Run the workflow from the release tag, for example `vX.Y.Z`.
4. Set `publish_to_testpypi` to `true`.
5. Keep `publish_to_pypi` set to `false`.
6. Approve the `testpypi` environment if GitHub asks for approval.

You can also use GitHub CLI after the trusted publisher exists:

```bash
gh workflow run publish.yml \
  --repo marmar9615-cloud/stui-terminal \
  --ref vX.Y.Z \
  -f publish_to_testpypi=true \
  -f publish_to_pypi=false
```

## Trigger PyPI Publish

After the PyPI Trusted Publisher is configured and local verification is green:

1. Go to GitHub Actions for this repository.
2. Select the `Publish` workflow.
3. Run the workflow from the release tag, for example `vX.Y.Z`.
4. Keep `publish_to_testpypi` set to `false`.
5. Set `publish_to_pypi` to `true`.

You can also use GitHub CLI after the trusted publisher exists:

```bash
gh workflow run publish.yml \
  --repo marmar9615-cloud/stui-terminal \
  --ref vX.Y.Z \
  -f publish_to_testpypi=false \
  -f publish_to_pypi=true
```

## Verify TestPyPI Install

Download only the exact TestPyPI wheel into a new private directory. Install
that local wheel while resolving its dependencies exclusively from production
PyPI; do not combine TestPyPI and PyPI as competing resolver indexes.

```bash
TESTPYPI_TMP="$(mktemp -d "${TMPDIR:-/tmp}/stui-testpypi.XXXXXX")"
trap 'rm -rf "$TESTPYPI_TMP"' EXIT
mkdir -m 700 "$TESTPYPI_TMP/wheel"
python3.11 -m pip download \
  --index-url https://test.pypi.org/simple/ \
  --no-deps \
  --no-cache-dir \
  --only-binary=:all: \
  --dest "$TESTPYPI_TMP/wheel" \
  stui-terminal==X.Y.Z
TESTPYPI_WHEEL="$TESTPYPI_TMP/wheel/stui_terminal-X.Y.Z-py3-none-any.whl"
test -f "$TESTPYPI_WHEEL"
python3.11 -m venv "$TESTPYPI_TMP/venv"
. "$TESTPYPI_TMP/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install \
  --index-url https://pypi.org/simple/ \
  --no-cache-dir \
  "$TESTPYPI_WHEEL"
python -c "import stui; print(stui.__version__)"
stui --version
```

Expected version for this release:

```text
X.Y.Z
stui X.Y.Z
```

## Verify PyPI Install

Use a clean temporary environment:

```bash
PYPI_TMP="$(mktemp -d "${TMPDIR:-/tmp}/stui-pypi.XXXXXX")"
trap 'rm -rf "$PYPI_TMP"' EXIT
python3.11 -m venv "$PYPI_TMP/venv"
. "$PYPI_TMP/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install \
  --index-url https://pypi.org/simple/ \
  --no-cache-dir \
  stui-terminal==X.Y.Z
python -c "import stui; print(stui.__version__)"
stui --version
stui selftest
stui selftest --strict
stui init "$PYPI_TMP/stui-app.py"
stui check "$PYPI_TMP/stui-app.py" --strict
stui init "$PYPI_TMP/stui-data-app.py" --template data
stui check "$PYPI_TMP/stui-data-app.py" --strict
stui init "$PYPI_TMP/stui-charts-app.py" --template charts
stui check "$PYPI_TMP/stui-charts-app.py" --strict
```

For v2.2.0, finish with an exact-version API probe from that fresh PyPI
environment:

```bash
python - <<'PY'
import stui as st

assert callable(st.cache_data)
assert callable(st.cache_resource)
assert callable(st.text_area)
assert st.__version__ == "2.2.0"
print(st.__version__)
PY
stui example copy caching "$PYPI_TMP/caching-v220.py"
stui example copy prompt_workbench "$PYPI_TMP/prompt-workbench-v220.py"
stui check "$PYPI_TMP/caching-v220.py" --strict --repeat 2
stui check "$PYPI_TMP/prompt-workbench-v220.py" --strict --repeat 2
```

For v2.3.0, also run this exact-version installed proof:

```bash
python - <<'PY'
import stui as st

for name in (
    "cache_data", "cache_resource", "text_area", "toggle",
    "tabs", "path_input", "data_table",
):
    assert callable(getattr(st, name)), name
assert st.__version__ == "2.3.0"
PY
stui demo list
stui example copy workspace "$PYPI_TMP/workspace.py"
stui init "$PYPI_TMP/workspace-init.py" --template workspace
stui check "$PYPI_TMP/workspace.py" --strict --repeat 3
stui inspect "$PYPI_TMP/workspace.py" --strict --repeat 3 --json
stui selftest --strict --repeat 2 --json
```

The `stui.inspect.v1` JSON must parse without any prefix or suffix from app
stdout/stderr and must not contain rendered values, session values, cache
arguments/results, environment values, or file contents.

Run the copied examples interactively when a real terminal is available. If
automation cannot close them reliably, use the Textual harness and record the
exact limitation instead of claiming an unobserved manual pass.
