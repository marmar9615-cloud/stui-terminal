#!/usr/bin/env sh
set -eu

PYTHON_CMD="${PYTHON:-python3.11}"
CREATED_WORKDIR=0
if [ -n "${STUI_CUSTOM_PROJECT_DIR:-}" ]; then
  WORKDIR="$STUI_CUSTOM_PROJECT_DIR"
else
  WORKDIR="$(mktemp -d /tmp/stui-custom-project.XXXXXX)"
  CREATED_WORKDIR=1
fi
mkdir -p "$WORKDIR"
cleanup() {
  if [ "$CREATED_WORKDIR" -eq 1 ]; then
    rm -rf "$WORKDIR"
  fi
}
trap cleanup EXIT

if [ -n "${STUI_WHEEL:-}" ]; then
  "$PYTHON_CMD" -m venv "$WORKDIR/.venv"
  PY="$WORKDIR/.venv/bin/python"
  STUI_BIN="$WORKDIR/.venv/bin/stui"
  "$PY" -m pip install --upgrade pip >/dev/null
  "$PY" -m pip install "$STUI_WHEEL" >/dev/null
else
  PY="$PYTHON_CMD"
  STUI_BIN="$PYTHON_CMD -m stui"
fi

mkdir -p "$WORKDIR/my_project"
cat > "$WORKDIR/my_project/__init__.py" <<'PY'
"""Tiny external project package used by stui release validation."""
PY

cat > "$WORKDIR/my_project/data.py" <<'PY'
from collections import namedtuple
from dataclasses import dataclass


@dataclass
class Run:
    name: str
    score: float
    notes: str


Point = namedtuple("Point", ["x", "y"])


def rows():
    return [
        {"step": 1, "loss": 0.9, "accuracy": 0.42, "phase": "warmup"},
        {"step": 2, "loss": 0.5, "accuracy": 0.71},
        {"step": 3, "loss": 0.25, "accuracy": 0.83, "phase": "eval"},
    ]


def object_rows():
    return [
        Run("local", 0.91, "line one\nline two"),
        Point("wheel", 0.87),
    ]


def project_name():
    return "external project"
PY

cat > "$WORKDIR/app.py" <<'PY'
import stui as st

from my_project.data import object_rows, project_name, rows

st.title("Custom validation")
st.write("Project:", project_name())
left, right = st.columns(2)
with left:
    st.metric("Runs", 3, "+1")
    st.table(rows(), max_rows=2, max_cols=2)
with right:
    st.dataframe(object_rows(), max_rows=2, max_cols=3)
    st.bar_chart({"passed": 12, "failed": -1})
    st.line_chart(rows())
with st.status("Validation status", state="complete", expanded=True):
    st.help("This app validates installed-package runtime behavior.")
st.success("custom project rendered")
PY

(
  cd "$WORKDIR"
  if [ -n "${STUI_WHEEL:-}" ]; then
    env -u PYTHONPATH "$STUI_BIN" --version >/dev/null
    env -u PYTHONPATH "$STUI_BIN" doctor --json >/dev/null
    env -u PYTHONPATH "$STUI_BIN" selftest --strict --repeat 2 --json > selftest-result.json
    env -u PYTHONPATH "$STUI_BIN" check app.py --strict --repeat 2 --json > check-result.json
  else
    env -u PYTHONPATH "$PY" -m stui --version >/dev/null
    env -u PYTHONPATH "$PY" -m stui doctor --json >/dev/null
    env -u PYTHONPATH "$PY" -m stui selftest --strict --repeat 2 --json > selftest-result.json
    env -u PYTHONPATH "$PY" -m stui check app.py --strict --repeat 2 --json > check-result.json
  fi
)

"$PY" - "$WORKDIR/selftest-result.json" <<'PY'
import json
import pathlib
import sys

result_path = pathlib.Path(sys.argv[1])
payload = json.loads(result_path.read_text(encoding="utf-8"))

assert payload["schema_version"] == "stui.selftest.v1", payload
assert payload["ok"] is True, payload
assert payload["strict"] is True, payload
assert payload["repeat"] == 2, payload
assert payload["summary"]["passed"] == payload["summary"]["total"], payload
PY

"$PY" - "$WORKDIR/check-result.json" <<'PY'
import json
import pathlib
import sys

result_path = pathlib.Path(sys.argv[1])
payload = json.loads(result_path.read_text(encoding="utf-8"))

assert payload["schema_version"] == "stui.check.v1", payload
assert payload["ok"] is True, payload
assert payload["strict"] is True, payload
assert payload["summary"]["runs_requested"] == 2, payload
assert payload["summary"]["runs_completed"] == 2, payload
assert payload["status"] == "ok", payload
assert payload["exit_code"] == 0, payload
assert payload["summary"]["warning_count"] == 0, payload
assert payload["script"]["path"].endswith("/app.py"), payload
types = payload["summary"]["element_types"]
for required in [
    "TitleElement",
    "WriteElement",
    "ColumnsElement",
    "MetricElement",
    "TableElement",
    "BarChartElement",
    "LineChartElement",
    "StatusElement",
    "HelpElement",
    "AlertElement",
]:
    assert types.get(required, 0) >= 1, types
assert payload["summary"]["error_count"] == 0, payload
PY

echo "custom project validation passed: $WORKDIR"
