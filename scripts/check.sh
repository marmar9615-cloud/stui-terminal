#!/usr/bin/env sh
set -eu

if [ -z "${PYTHON:-}" ] && [ -x ".venv/bin/python3.11" ]; then
  PYTHON="$(pwd -P)/.venv/bin/python3.11"
else
  PYTHON="${PYTHON:-python3.11}"
fi

"$PYTHON" -m ruff check .
"$PYTHON" -m pytest
PYTHON="$PYTHON" ./scripts/verify_custom_project.sh
