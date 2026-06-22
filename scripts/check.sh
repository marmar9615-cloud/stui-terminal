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
"$PYTHON" -m stui selftest --strict --json >/tmp/stui-selftest-result.json
PYTHON="$PYTHON" ./scripts/verify_custom_project.sh
if [ -d dist ] && ls dist/stui_terminal-* >/dev/null 2>&1; then
  "$PYTHON" scripts/audit_package_contents.py dist
fi
