from pathlib import Path

from typer.testing import CliRunner

from stui import cli


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
    assert "stui 0.2.0rc1" in result.output


def test_doctor_command() -> None:
    result = CliRunner().invoke(cli.app, ["doctor"])

    assert result.exit_code == 0
    assert "stui:" in result.output
    assert "python:" in result.output
    assert "textual:" in result.output


def test_examples_command() -> None:
    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "stui run examples/basic.py" in result.output
    assert "stui run examples/dashboard.py" in result.output
