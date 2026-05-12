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
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check .
python -m pytest
python -m build
python -m twine check dist/*
stui --version
python -m stui --version
```

## Trigger TestPyPI Publish

After the TestPyPI Trusted Publisher is configured:

1. Go to GitHub Actions for this repository.
2. Select the `Publish` workflow.
3. Run the workflow from the release tag, for example `v0.9.0`.
4. Set `publish_to_testpypi` to `true`.
5. Keep `publish_to_pypi` set to `false`.
6. Approve the `testpypi` environment if GitHub asks for approval.

You can also use GitHub CLI after the trusted publisher exists:

```bash
gh workflow run publish.yml \
  --repo marmar9615-cloud/stui-terminal \
  --ref v0.9.0 \
  -f publish_to_testpypi=true \
  -f publish_to_pypi=false
```

## Trigger PyPI Publish

After the PyPI Trusted Publisher is configured and local verification is green:

1. Go to GitHub Actions for this repository.
2. Select the `Publish` workflow.
3. Run the workflow from the release tag, for example `v0.9.0`.
4. Keep `publish_to_testpypi` set to `false`.
5. Set `publish_to_pypi` to `true`.

You can also use GitHub CLI after the trusted publisher exists:

```bash
gh workflow run publish.yml \
  --repo marmar9615-cloud/stui-terminal \
  --ref v0.9.0 \
  -f publish_to_testpypi=false \
  -f publish_to_pypi=true
```

## Verify TestPyPI Install

Use a clean temporary environment:

```bash
python3.11 -m venv /tmp/stui-terminal-testpypi
. /tmp/stui-terminal-testpypi/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  stui-terminal==0.9.0
python -c "import stui; print(stui.__version__)"
stui --version
```

Expected version for this release:

```text
0.9.0
stui 0.9.0
```

## Verify PyPI Install

Use a clean temporary environment:

```bash
python3.11 -m venv /tmp/stui-terminal-pypi
. /tmp/stui-terminal-pypi/bin/activate
python -m pip install --upgrade pip
python -m pip install stui-terminal==0.9.0
python -c "import stui; print(stui.__version__)"
stui --version
```
