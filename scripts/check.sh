#!/usr/bin/env sh
set -eu

if [ -z "${PYTHON:-}" ] && [ -x ".venv/bin/python3.11" ]; then
  PYTHON="$(pwd -P)/.venv/bin/python3.11"
else
  PYTHON="${PYTHON:-python3.11}"
fi

"$PYTHON" -m ruff check .
"$PYTHON" scripts/check_release_version.py
"$PYTHON" -m pytest
SELFTEST_RESULT="$(mktemp /tmp/stui-selftest-result.XXXXXX.json)"
trap 'rm -f "$SELFTEST_RESULT"' EXIT
"$PYTHON" -m stui selftest --strict --repeat 2 --json >"$SELFTEST_RESULT"
PYTHON="$PYTHON" ./scripts/verify_custom_project.sh
if [ -d dist ] && ls dist/stui_terminal-* >/dev/null 2>&1; then
  VERSION="$("$PYTHON" -c 'import stui; print(stui.__version__)')"
  "$PYTHON" scripts/audit_package_contents.py dist --version "$VERSION"
  "$PYTHON" scripts/verify_installed_smoke.py dist
  WHEEL="$(ls "dist/stui_terminal-${VERSION}-"*.whl)"
  "$PYTHON" scripts/verify_v230_project.py --wheel "$WHEEL"
fi
