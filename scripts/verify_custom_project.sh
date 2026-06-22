#!/usr/bin/env sh
set -eu

PYTHON_CMD="${PYTHON:-python3.11}"
WORKDIR="${STUI_CUSTOM_PROJECT_DIR:-$(mktemp -d /tmp/stui-custom-project.XXXXXX)}"
mkdir -p "$WORKDIR"

if [ -n "${STUI_WHEEL:-}" ]; then
  "$PYTHON_CMD" -m venv "$WORKDIR/.venv"
  PY="$WORKDIR/.venv/bin/python"
  "$PY" -m pip install --upgrade pip >/dev/null
  "$PY" -m pip install "$STUI_WHEEL" >/dev/null
else
  PY="$PYTHON_CMD"
fi

cat > "$WORKDIR/helper.py" <<'PY'
def rows():
    return [
        {"step": 1, "loss": 0.9, "accuracy": 0.42},
        {"step": 2, "loss": 0.5, "accuracy": 0.71},
        {"step": 3, "loss": 0.25, "accuracy": 0.83},
    ]


def project_name():
    return "external project"
PY

cat > "$WORKDIR/app.py" <<'PY'
import stui as st

from helper import project_name, rows

st.title("Custom validation")
st.write("Project:", project_name())
left, right = st.columns(2)
with left:
    st.metric("Runs", 3, "+1")
    st.table(rows(), max_rows=2, max_cols=2)
with right:
    st.bar_chart({"passed": 12, "failed": -1})
    st.line_chart(rows())
with st.status("Validation status", state="complete", expanded=True):
    st.help("This app validates installed-package runtime behavior.")
st.success("custom project rendered")
PY

(
  cd "$WORKDIR"
  env -u PYTHONPATH "$PY" -m stui check app.py --json > check-result.json
)

"$PY" - "$WORKDIR/check-result.json" <<'PY'
import json
import pathlib
import sys

result_path = pathlib.Path(sys.argv[1])
payload = json.loads(result_path.read_text(encoding="utf-8"))

assert payload["schema_version"] == "stui.check.v1", payload
assert payload["ok"] is True, payload
assert payload["status"] == "ok", payload
assert payload["exit_code"] == 0, payload
assert payload["script"]["path"].endswith("/app.py"), payload
types = payload["summary"]["element_types"]
for required in [
    "TitleElement",
    "WriteElement",
    "ColumnsElement",
    "StatusElement",
    "AlertElement",
]:
    assert types.get(required, 0) >= 1, types
assert payload["summary"]["error_count"] == 0, payload
PY

echo "custom project validation passed: $WORKDIR"
