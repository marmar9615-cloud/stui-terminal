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
    assert "stui 0.4.0" in result.output


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
    assert "capabilities:" in result.output
    assert "examples:" in result.output
    assert "example source:" in result.output


def test_examples_command() -> None:
    result = CliRunner().invoke(cli.app, ["examples"])

    assert result.exit_code == 0
    assert "basic [bundled + repo" in result.output
    assert "run:  stui run" in result.output
    assert "copy: stui example copy basic ./examples/basic.py" in result.output
    assert "kitchen_sink [bundled + repo" in result.output


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
    assert "repo_only [repo-only" in result.output
    assert "copy:" not in result.output


def test_example_copy_writes_bundled_example(tmp_path: Path) -> None:
    dest = tmp_path / "basic.py"

    result = CliRunner().invoke(cli.app, ["example", "copy", "basic", str(dest)])

    assert result.exit_code == 0
    assert "Copied basic.py" in result.output
    assert "st.title" in dest.read_text(encoding="utf-8")


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


def test_init_force_overwrites(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("# replace me\n", encoding="utf-8")

    result = CliRunner().invoke(cli.app, ["init", str(script), "--force"])

    assert result.exit_code == 0
    assert 'st.title("My stui app")' in script.read_text(encoding="utf-8")
