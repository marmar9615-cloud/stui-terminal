import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

import stui
from stui import cli


def _inspect_module():
    return importlib.import_module("stui.diagnostics")


def test_inspect_json_reports_versioned_non_sensitive_runtime_diagnostics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("STUI_INSPECT_SECRET", "environment-secret")
    helper = tmp_path / "inspect_helper.py"
    helper.write_text(
        """
import stui as st

@st.cache_data
def load(value):
    return {"cached": value}
""",
        encoding="utf-8",
    )
    script = tmp_path / "app.py"
    script.write_text(
        """
import stui as st
from inspect_helper import load

st.session_state["private-state-key"] = "session-secret"

st.title("rendered-secret")
with st.container():
    st.button("Run", key="run")
    left, right = st.columns(2)
    with left:
        st.write(load("cache-argument-secret"))
    with right:
        st.checkbox("Ready", key="ready")
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli.app,
        ["inspect", str(script), "--repeat", "2", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["schema_version"] == "stui.inspect.v1"
    assert payload["ok"] is True
    assert payload["strict"] is False
    assert payload["status"] == "ok"
    assert payload["exit_code"] == 0
    assert payload["versions"]["stui"] == stui.__version__
    assert set(payload["versions"]) == {"stui", "python", "textual", "rich", "typer"}
    assert payload["paths"] == {
        "input": str(script),
        "script": str(script.resolve()),
        "project_root": str(tmp_path.resolve()),
        "local_modules": [
            {"name": "inspect_helper", "path": str(helper.resolve())}
        ],
        "watch_files": [str(script.resolve()), str(helper.resolve())],
    }
    assert payload["timings"]["total_ms"] >= 0
    assert len(payload["timings"]["runs"]) == 2
    assert all(run["duration_ms"] >= 0 for run in payload["timings"]["runs"])

    summary = payload["summary"]
    assert summary["runs_requested"] == 2
    assert summary["runs_completed"] == 2
    assert summary["element_count"] == 6
    assert summary["total_element_count"] == 12
    assert summary["element_types"] == {
        "ButtonElement": 1,
        "CheckboxElement": 1,
        "ColumnsElement": 1,
        "ContainerElement": 1,
        "TitleElement": 1,
        "WriteElement": 1,
    }
    assert summary["widget_count"] == 2
    assert summary["total_widget_count"] == 4
    assert summary["widget_types"] == {
        "ButtonElement": 1,
        "CheckboxElement": 1,
    }
    assert summary["key_counts"] == {
        "session": 2,
        "widgets": 2,
        "explicit_widgets": 2,
        "forms": 0,
        "elements": 2,
    }
    assert summary["nesting"] == {
        "max_depth": 2,
        "nested_elements": 4,
        "containers": 1,
        "column_groups": 1,
        "columns": 2,
        "by_depth": {"0": 2, "1": 2, "2": 2},
    }
    assert summary["local_module_count"] == 1
    assert summary["watch_file_count"] == 2
    assert summary["cache"] == {
        "schema_version": "stui.cache_info.v1",
        "data": {"functions": 1, "entries": 1, "in_flight": 0},
        "resource": {"functions": 0, "entries": 0, "in_flight": 0},
        "total": {"functions": 1, "entries": 1, "in_flight": 0},
    }
    assert summary["warning_count"] == 0
    assert summary["error_count"] == 0
    assert len(payload["runs"]) == 2
    assert all(run["element_count"] == 6 for run in payload["runs"])
    assert payload["warnings"] == []
    assert payload["errors"] == []

    for secret in (
        "private-state-key",
        "session-secret",
        "environment-secret",
        "rendered-secret",
        "cache-argument-secret",
    ):
        assert secret not in result.output


def test_inspect_strict_fails_on_structured_warning_without_source_values(
    tmp_path: Path,
) -> None:
    script = tmp_path / "empty.py"
    script.write_text(
        "import stui as st\nsecret = 'file-value-secret'\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli.app,
        ["inspect", str(script), "--strict", "--json"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["strict"] is True
    assert payload["status"] == "ok"
    assert payload["exit_code"] == 1
    assert payload["warnings"] == [{"code": "empty_output", "run": 1}]
    assert payload["errors"] == []
    assert payload["summary"]["warning_count"] == 1
    assert "file-value-secret" not in result.output


def test_inspect_reports_script_error_without_exception_message(tmp_path: Path) -> None:
    script = tmp_path / "error.py"
    script.write_text(
        "raise RuntimeError('exception-secret')\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(cli.app, ["inspect", str(script), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["status"] == "script_error"
    assert payload["exit_code"] == 1
    assert payload["errors"] == [{"code": "script_error", "run": 1}]
    assert payload["summary"]["error_count"] == 1
    assert payload["summary"]["element_types"] == {"ErrorElement": 1}
    assert "exception-secret" not in result.output
    assert "Traceback" not in result.output


def test_inspect_repeat_stops_on_first_script_error(tmp_path: Path) -> None:
    script = tmp_path / "repeat_error.py"
    script.write_text(
        """
import stui as st

st.session_state.count = st.session_state.get("count", 0) + 1
if st.session_state.count == 2:
    raise RuntimeError("repeat-secret")
st.write("ok")
""",
        encoding="utf-8",
    )

    report = _inspect_module().inspect_script(script, repeat=3)

    assert report["status"] == "script_error"
    assert report["summary"]["runs_requested"] == 3
    assert report["summary"]["runs_completed"] == 2
    assert [run["run"] for run in report["runs"]] == [1, 2]
    assert report["errors"] == [{"code": "script_error", "run": 2}]
    assert "repeat-secret" not in json.dumps(report)


def test_inspect_json_reports_invalid_script_without_reading_it() -> None:
    result = CliRunner().invoke(cli.app, ["inspect", "missing.py", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["schema_version"] == "stui.inspect.v1"
    assert payload["ok"] is False
    assert payload["status"] == "invalid_script"
    assert payload["exit_code"] == 2
    assert payload["paths"] == {
        "input": "missing.py",
        "script": None,
        "project_root": None,
        "local_modules": [],
        "watch_files": [],
    }
    assert payload["summary"]["runs_completed"] == 0
    assert payload["errors"] == [{"code": "missing", "run": None}]


def test_inspect_human_output_has_operational_summary_without_rendered_values(
    tmp_path: Path,
) -> None:
    script = tmp_path / "human.py"
    script.write_text(
        "import stui as st\nst.write('human-output-secret')\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(cli.app, ["inspect", str(script)])

    assert result.exit_code == 0
    assert "stui inspect passed:" in result.output
    assert "schema: stui.inspect.v1" in result.output
    assert "versions:" in result.output
    assert "runs: 1/1" in result.output
    assert "elements: 1 current, 1 total" in result.output
    assert "widgets: 0 current, 0 total" in result.output
    assert "nesting:" in result.output
    assert "cache:" in result.output
    assert "watch files: 1" in result.output
    assert "human-output-secret" not in result.output
