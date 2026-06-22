import json
import os
import subprocess
import sys
from os import terminal_size
from pathlib import Path

from typer.testing import CliRunner

import stui
from stui import cli
from stui.elements import ErrorElement
from stui.runtime import Runtime


def test_run_launches_existing_script(monkeypatch, tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("import stui as st\nst.write('hello')\n", encoding="utf-8")
    launched: list[Path] = []

    class FakeRuntime:
        def __init__(self, script_path: Path) -> None:
            self.script_path = script_path

    class FakeApp:
        def __init__(self, runtime: FakeRuntime) -> None:
            self.runtime = runtime

        def run(self) -> None:
            launched.append(self.runtime.script_path)

    monkeypatch.setattr(cli, "Runtime", FakeRuntime)
    monkeypatch.setattr(cli, "StuiApp", FakeApp)

    result = CliRunner().invoke(cli.app, ["run", str(script)])

    assert result.exit_code == 0
    assert launched == [script.resolve()]


def test_run_rejects_missing_file() -> None:
    result = CliRunner().invoke(cli.app, ["run", "missing.py"])

    assert result.exit_code != 0
    assert "file does not exist: missing.py" in result.output


def test_run_missing_repo_example_guides_installed_users(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["run", "examples/basic.py"])

    assert result.exit_code != 0
    normalized_output = " ".join(result.output.split())
    assert "file does not exist: examples/basic.py" in result.output
    assert "Bundled examples are available after installation" in result.output
    assert "stui example copy basic" in normalized_output
    assert "examples/basic.py" in normalized_output
    assert "stui run examples/basic.py" in normalized_output


def test_run_missing_unknown_repo_example_stays_plain(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["run", "examples/not_bundled.py"])

    assert result.exit_code != 0
    assert "file does not exist: examples/not_bundled.py" in result.output
    assert "Bundled examples are available after installation" not in result.output


def test_demo_list_prints_supported_demos() -> None:
    result = CliRunner().invoke(cli.app, ["demo", "list"])

    assert result.exit_code == 0
    assert "stui demos:" in result.output
    assert "basic - Smallest useful app:" in result.output
    assert "dashboard - Dashboard-style layout" in result.output
    assert "forms - Form-style user input flow." in result.output
    assert "charts - Simple chart and data visualization patterns." in result.output
    assert "kitchen_sink - Broad API tour" in result.output
    assert "counter" not in result.output


def test_demo_list_only_prints_available_bundled_demo_resources(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_bundled_examples", lambda: {"basic.py"})

    result = CliRunner().invoke(cli.app, ["demo", "list"])

    assert result.exit_code == 0
    assert "basic - Smallest useful app:" in result.output
    assert "dashboard" not in result.output
    assert "forms" not in result.output


def test_demo_list_reports_when_no_bundled_resources(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_bundled_examples", lambda: set())

    result = CliRunner().invoke(cli.app, ["demo", "list"])

    assert result.exit_code == 0
    assert "No bundled demos were found" in result.output


def test_demo_launches_valid_bundled_demo(monkeypatch) -> None:
    launched: list[Path] = []

    class FakeRuntime:
        def __init__(self, script_path: Path) -> None:
            self.script_path = script_path

    class FakeApp:
        def __init__(self, runtime: FakeRuntime) -> None:
            self.runtime = runtime

        def run(self) -> None:
            launched.append(self.runtime.script_path)

    monkeypatch.setattr(cli, "Runtime", FakeRuntime)
    monkeypatch.setattr(cli, "StuiApp", FakeApp)

    result = CliRunner().invoke(cli.app, ["demo", "dashboard"])

    assert result.exit_code == 0
    assert [path.name for path in launched] == ["dashboard.py"]
    assert launched[0].exists()
    assert "stui/examples" in launched[0].as_posix()


def test_demo_rejects_invalid_demo_name() -> None:
    result = CliRunner().invoke(cli.app, ["demo", "counter"])
    normalized_output = " ".join(result.output.split())

    assert result.exit_code != 0
    assert "unknown demo 'counter'" in normalized_output
    assert "stui demo list" in result.output
    assert "basic, dashboard, forms, charts, kitchen_sink" in normalized_output


def test_demo_uses_package_resource_without_repo_checkout(
    monkeypatch,
    tmp_path: Path,
) -> None:
    launched: list[Path] = []

    class FakeRuntime:
        def __init__(self, script_path: Path) -> None:
            self.script_path = script_path

    class FakeApp:
        def __init__(self, runtime: FakeRuntime) -> None:
            self.runtime = runtime

        def run(self) -> None:
            launched.append(self.runtime.script_path)

    monkeypatch.setattr(cli, "Runtime", FakeRuntime)
    monkeypatch.setattr(cli, "StuiApp", FakeApp)
    monkeypatch.setattr(cli, "_examples_dir", lambda: Path("/missing/repo/examples"))

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli.app, ["demo", "forms"])

    assert result.exit_code == 0
    assert [path.name for path in launched] == ["forms.py"]
    assert launched[0].exists()
    assert "stui/examples" in launched[0].as_posix()


def test_run_rejects_directory(tmp_path: Path) -> None:
    result = CliRunner().invoke(cli.app, ["run", str(tmp_path)])

    assert result.exit_code != 0
    assert "not a file:" in result.output


def test_run_rejects_non_python_file(tmp_path: Path) -> None:
    script = tmp_path / "notes.txt"
    script.write_text("not python\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["run", str(script)])

    assert result.exit_code != 0
    assert "script must be a .py file:" in result.output


def test_version_option() -> None:
    result = CliRunner().invoke(cli.app, ["--version"])

    assert result.exit_code == 0
    assert f"stui {stui.__version__}" in result.output


def test_python_module_version_option() -> None:
    env = os.environ.copy()
    src_path = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONPATH"] = (
        src_path
        if not env.get("PYTHONPATH")
        else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    )
    result = subprocess.run(
        [sys.executable, "-m", "stui", "--version"],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )

    assert result.returncode == 0
    assert f"stui {stui.__version__}" in result.stdout
    assert result.stderr == ""


def test_doctor_command() -> None:
    result = CliRunner().invoke(cli.app, ["doctor"])

    assert result.exit_code == 0
    assert "stui:" in result.output
    assert "package:" in result.output
    assert "python:" in result.output
    assert "textual:" in result.output
    assert "rich:" in result.output
    assert "typer:" in result.output
    assert "terminal size:" in result.output
    assert "theme:" in result.output
    assert "TERM:" in result.output
    assert "COLORTERM:" in result.output
    assert "TERM_PROGRAM:" in result.output
    assert "STUI_THEME:" in result.output
    assert "NO_COLOR:" in result.output
    assert "capabilities:" in result.output
    assert "stdout_tty=" in result.output
    assert "stderr_tty=" in result.output
    assert "no_color_requested=" in result.output
    assert "examples:" in result.output
    assert "example source:" in result.output


def test_doctor_reports_terminal_environment(monkeypatch) -> None:
    monkeypatch.setattr(
        cli.shutil,
        "get_terminal_size",
        lambda fallback: terminal_size((100, 30)),
    )

    result = CliRunner().invoke(
        cli.app,
        ["doctor"],
        env={
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
            "TERM_PROGRAM": "Apple_Terminal",
            "STUI_THEME": "high-contrast",
            "NO_COLOR": "1",
        },
    )

    assert result.exit_code == 0
    assert "terminal size: 100x30 (ok)" in result.output
    assert "theme: high-contrast" in result.output
    assert "TERM: xterm-256color" in result.output
    assert "COLORTERM: truecolor" in result.output
    assert "TERM_PROGRAM: Apple_Terminal" in result.output
    assert "STUI_THEME: high-contrast" in result.output
    assert "NO_COLOR: yes" in result.output
    assert "color=truecolor" in result.output
    assert "no_color_requested=yes" in result.output


def test_doctor_warns_for_small_terminal(monkeypatch) -> None:
    monkeypatch.setattr(
        cli.shutil,
        "get_terminal_size",
        lambda fallback: terminal_size((60, 20)),
    )

    result = CliRunner().invoke(cli.app, ["doctor"])

    assert result.exit_code == 0
    assert (
        "terminal size: 60x20 (small; recommended at least 80x24)"
        in result.output
    )
    assert "warning: terminal is too small" in result.output


def test_doctor_json_output(monkeypatch) -> None:
    monkeypatch.setattr(
        cli.shutil,
        "get_terminal_size",
        lambda fallback: terminal_size((72, 24)),
    )

    result = CliRunner().invoke(
        cli.app,
        ["doctor", "--json"],
        env={
            "TERM": "dumb",
            "COLORTERM": "",
            "TERM_PROGRAM": "",
            "STUI_THEME": "not-a-theme",
            "NO_COLOR": "1",
        },
    )

    assert result.exit_code == 0
    diagnostics = json.loads(result.output)
    assert diagnostics["stui"] == stui.__version__
    assert diagnostics["terminal"]["columns"] == 72
    assert diagnostics["terminal"]["lines"] == 24
    assert diagnostics["terminal"]["too_small"] is True
    assert diagnostics["theme"] == "default"
    assert diagnostics["environment"]["TERM"] == "dumb"
    assert diagnostics["environment"]["STUI_THEME"] == "not-a-theme"
    assert diagnostics["environment"]["NO_COLOR"] == "1"
    assert diagnostics["capabilities"]["color"] == "none/dumb"
    assert diagnostics["capabilities"]["no_color_requested"] is True
    assert any("terminal is too small" in item for item in diagnostics["warnings"])
    assert any("TERM=dumb" in item for item in diagnostics["warnings"])


def test_doctor_json_warns_on_package_import_version_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_package_version", lambda name: "1.0.0")

    result = CliRunner().invoke(cli.app, ["doctor", "--json"])

    assert result.exit_code == 0
    diagnostics = json.loads(result.output)
    assert diagnostics["stui"] == stui.__version__
    assert diagnostics["package"] == "1.0.0"
    assert any(
        "imported stui version and stui-terminal distribution version differ"
        in item
        for item in diagnostics["warnings"]
    )
    assert "locations" in diagnostics


def test_color_capability_reports_truecolor_256_and_dumb() -> None:
    assert cli._color_capability("xterm-256color", "") == "256-color"
    assert cli._color_capability("xterm-256color", "truecolor") == "truecolor"
    assert cli._color_capability("dumb", "") == "none/dumb"


def test_examples_command() -> None:
    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "basic - Smallest useful app:" in result.output
    assert "bundled + repo" in result.output
    assert "repo run:     stui run" in result.output
    assert "copy:         stui example copy basic ./examples/basic.py" in result.output
    assert "kitchen_sink - Broad API tour" in result.output


def test_examples_command_does_not_claim_missing_wheel_examples(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_examples_dir", lambda: Path("/missing/examples"))
    monkeypatch.setattr(cli, "_bundled_examples", lambda: set())

    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "No bundled examples were found." in result.output
    assert "stui run examples/basic.py" not in result.output


def test_examples_command_marks_repo_only_examples(monkeypatch, tmp_path: Path) -> None:
    repo_examples = tmp_path / "examples"
    repo_examples.mkdir()
    (repo_examples / "repo_only.py").write_text("import stui as st\n", encoding="utf-8")
    monkeypatch.setattr(cli, "_examples_dir", lambda: repo_examples)
    monkeypatch.setattr(cli, "_bundled_examples", lambda: set())

    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "repo_only - Example app. [repo-only" in result.output
    assert "copy:" not in result.output


def test_examples_command_lists_bundled_without_repo(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_examples_dir", lambda: Path("/missing/examples"))
    monkeypatch.setattr(cli, "_bundled_examples", lambda: {"basic.py"})

    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "basic - Smallest useful app:" in result.output
    assert "[bundled]" in result.output
    assert (
        "bundled run:  stui example copy basic ./examples/basic.py "
        "&& stui run ./examples/basic.py"
    ) in result.output


def test_example_list_prints_bundled_names() -> None:
    result = CliRunner().invoke(cli.app, ["example", "list"])

    assert result.exit_code == 0
    assert "basic" in result.output
    assert "dashboard" in result.output


def test_example_copy_writes_bundled_example(tmp_path: Path) -> None:
    dest = tmp_path / "basic.py"

    result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])

    assert result.exit_code == 0
    assert "Copied basic.py" in result.output
    assert 'st.title("stui demo")' in dest.read_text(encoding="utf-8")


def test_example_copy_basic_app_runs_without_script_errors(tmp_path: Path) -> None:
    dest = tmp_path / "basic.py"

    copy_result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])
    runtime = Runtime(dest)
    elements = runtime.run_script()

    assert copy_result.exit_code == 0
    assert not any(isinstance(element, ErrorElement) for element in elements)


def test_example_copy_rejects_unknown_example() -> None:
    result = CliRunner().invoke(cli.app, ["example", "copy", "missing", "missing.py"])
    normalized_output = " ".join(result.output.split())

    assert result.exit_code != 0
    assert "unknown bundled" in normalized_output
    assert "'missing'" in normalized_output
    assert "stui example list" in result.output


def test_example_copy_rejects_overwrite_without_force(tmp_path: Path) -> None:
    dest = tmp_path / "basic.py"
    dest.write_text("# keep me\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])

    assert result.exit_code != 0
    assert "destination exists:" in result.output
    assert dest.read_text(encoding="utf-8") == "# keep me\n"


def test_example_copy_force_overwrites(tmp_path: Path) -> None:
    dest = tmp_path / "basic.py"
    dest.write_text("# replace me\n", encoding="utf-8")

    result = CliRunner().invoke(
        cli.app,
        ["example", "copy", "basic", str(dest), "--force"],
    )

    assert result.exit_code == 0
    assert "st.title" in dest.read_text(encoding="utf-8")


def test_example_copy_into_existing_directory(tmp_path: Path) -> None:
    dest = tmp_path / "examples"
    dest.mkdir()

    result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])

    copied = dest / "basic.py"
    assert result.exit_code == 0
    assert copied.exists()
    assert "Copied basic.py" in result.output


def test_example_copy_into_directory_rejects_existing_child_without_force(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "examples"
    dest.mkdir()
    child = dest / "basic.py"
    child.write_text("# keep me\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])

    assert result.exit_code != 0
    assert "destination exists:" in result.output
    assert child.read_text(encoding="utf-8") == "# keep me\n"


def test_example_copy_into_directory_force_overwrites_existing_child(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "examples"
    dest.mkdir()
    child = dest / "basic.py"
    child.write_text("# replace me\n", encoding="utf-8")

    result = CliRunner().invoke(
        cli.app,
        ["example", "copy", "basic", str(dest), "--force"],
    )

    assert result.exit_code == 0
    assert "st.title" in child.read_text(encoding="utf-8")


def test_init_creates_app(tmp_path: Path) -> None:
    script = tmp_path / "app.py"

    result = CliRunner().invoke(cli.app, ["init", str(script)])

    assert result.exit_code == 0
    content = script.read_text(encoding="utf-8")
    assert 'st.title("My stui app")' in content
    assert "stui run app.py" in content


def test_init_rejects_overwrite_without_force(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("# keep me\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["init", str(script)])

    assert result.exit_code != 0
    assert "file exists:" in result.output
    assert script.read_text(encoding="utf-8") == "# keep me\n"


def test_init_rejects_directory_even_with_py_suffix(tmp_path: Path) -> None:
    script_dir = tmp_path / "app.py"
    script_dir.mkdir()

    result = CliRunner().invoke(cli.app, ["init", str(script_dir), "--force"])

    assert result.exit_code != 0
    assert "not a file:" in result.output


def test_init_force_overwrites(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("# replace me\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["init", str(script), "--force"])

    assert result.exit_code == 0
    assert 'st.title("My stui app")' in script.read_text(encoding="utf-8")


def test_init_dashboard_template(tmp_path: Path) -> None:
    script = tmp_path / "dashboard.py"

    result = CliRunner().invoke(
        cli.app,
        ["init", str(script), "--template", "dashboard"],
    )

    assert result.exit_code == 0
    content = script.read_text(encoding="utf-8")
    assert 'st.title("Team dashboard")' in content
    assert 'st.metric("Builds", "18", "+3")' in content
    assert "from the dashboard template" in result.output


def test_init_dashboard_template_runs_without_script_errors(tmp_path: Path) -> None:
    script = tmp_path / "dashboard.py"

    result = CliRunner().invoke(
        cli.app,
        ["init", str(script), "--template", "dashboard"],
    )
    runtime = Runtime(script)
    elements = runtime.run_script()

    assert result.exit_code == 0
    assert not any(isinstance(element, ErrorElement) for element in elements)


def test_init_forms_template_long_option(tmp_path: Path) -> None:
    script = tmp_path / "signup.py"

    result = CliRunner().invoke(
        cli.app,
        ["init", str(script), "--template", "forms"],
    )

    assert result.exit_code == 0
    content = script.read_text(encoding="utf-8")
    assert 'st.title("Signup form")' in content
    assert "st.checkbox" in content


def test_init_forms_template_short_option(tmp_path: Path) -> None:
    script = tmp_path / "signup.py"

    result = CliRunner().invoke(cli.app, ["init", str(script), "-t", "forms"])

    assert result.exit_code == 0
    content = script.read_text(encoding="utf-8")
    assert 'st.title("Signup form")' in content
    assert "st.checkbox" in content


def test_init_forms_template_runs_without_script_errors(tmp_path: Path) -> None:
    script = tmp_path / "signup.py"

    result = CliRunner().invoke(
        cli.app,
        ["init", str(script), "--template", "forms"],
    )
    runtime = Runtime(script)
    elements = runtime.run_script()

    assert result.exit_code == 0
    assert not any(isinstance(element, ErrorElement) for element in elements)


def test_all_init_templates_run_without_script_errors(tmp_path: Path) -> None:
    for template in cli.INIT_TEMPLATE_CHOICES:
        script = tmp_path / f"{template}.py"

        result = CliRunner().invoke(
            cli.app,
            ["init", str(script), "--template", template],
        )
        runtime = Runtime(script)
        elements = runtime.run_script()

        assert result.exit_code == 0, result.output
        assert not any(isinstance(element, ErrorElement) for element in elements), (
            template
        )


def test_init_rejects_unknown_template(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        cli.app,
        ["init", str(tmp_path / "app.py"), "--template", "unknown"],
    )
    normalized_output = " ".join(result.output.split())

    assert result.exit_code != 0
    assert "unknown template 'unknown'" in normalized_output
    assert "basic, dashboard," in normalized_output
    assert "forms" in normalized_output
