from __future__ import annotations

import json as json_module
import os
import platform
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .app import StuiApp, resolve_theme
from .elements import ErrorElement
from .runtime import Runtime

app = typer.Typer(
    add_completion=False,
    help="Run tiny Streamlit-inspired terminal UI apps.",
)

EXAMPLE_NAMES = (
    "basic.py",
    "counter.py",
    "model_demo.py",
    "inputs.py",
    "data_display.py",
    "dashboard.py",
    "forms.py",
    "layouts.py",
    "charts.py",
    "kitchen_sink.py",
)

MIN_TERMINAL_COLUMNS = 80
MIN_TERMINAL_LINES = 24

EXAMPLE_DESCRIPTIONS = {
    "basic.py": "Smallest useful app: title, text, input, button, and feedback.",
    "counter.py": "Session-state counter with button interactions.",
    "model_demo.py": "Compact model comparison demo with inputs and metrics.",
    "inputs.py": "Input widgets for forms and simple settings.",
    "data_display.py": "Tables, metrics, and structured output examples.",
    "dashboard.py": "Dashboard-style layout with metrics and status sections.",
    "forms.py": "Form-style user input flow.",
    "layouts.py": "Columns, containers, and page organization.",
    "charts.py": "Simple chart and data visualization patterns.",
    "kitchen_sink.py": "Broad API tour for trying many widgets at once.",
}

DEMO_NAMES = (
    "basic",
    "dashboard",
    "forms",
    "charts",
    "kitchen_sink",
)

INIT_TEMPLATES = {
    "basic": '''import stui as st

st.title("My stui app")
st.write("Edit this file, then run:")
st.code("stui run {filename}")

name = st.text_input("Name", value="friend")

if st.button("Greet"):
    st.success(f"Hello, {{name}}!")
''',
    "dashboard": '''import stui as st

st.title("Team dashboard")
st.write("Edit this file, then run:")
st.code("stui run {filename}")

st.header("Today")
st.metric("Builds", "18", "+3")
st.metric("Open issues", "7", "-2")
st.metric("Deploys", "4", "+1")

st.divider()
st.subheader("Status")
st.success("API healthy")
st.info("Next release window: Friday")
st.warning("Review queue needs attention")
''',
    "forms": '''import stui as st

st.title("Signup form")
st.write("Edit this file, then run:")
st.code("stui run {filename}")

name = st.text_input("Name")
email = st.text_input("Email")
wants_updates = st.checkbox("Send me product updates", value=True)

if st.button("Submit"):
    if name and email:
        st.success(f"Thanks, {{name}}. Saved {{email}}.")
        if wants_updates:
            st.info("Product updates are enabled.")
    else:
        st.error("Name and email are required.")
''',
}

INIT_TEMPLATE_CHOICES = tuple(INIT_TEMPLATES)


@dataclass(frozen=True)
class ExampleInfo:
    name: str
    bundled: bool
    repo_path: Path | None


def _examples_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "examples"


def _bundled_examples() -> set[str]:
    try:
        examples = resources.files("stui.examples")
    except ModuleNotFoundError:
        return set()
    return {
        child.name
        for child in examples.iterdir()
        if child.name.endswith(".py") and child.name != "__init__.py"
    }


def _example_name(name: str) -> str:
    return name if name.endswith(".py") else f"{name}.py"


def _example_infos() -> list[ExampleInfo]:
    examples_dir = _examples_dir()
    bundled = _bundled_examples()
    repo = {
        path.name
        for path in examples_dir.glob("*.py")
        if examples_dir.exists() and path.name != "__init__.py"
    }
    names = [name for name in EXAMPLE_NAMES if name in bundled or name in repo]
    names.extend(sorted((bundled | repo) - set(names)))
    return [
        ExampleInfo(
            name=name,
            bundled=name in bundled,
            repo_path=(examples_dir / name) if name in repo else None,
        )
        for name in names
    ]


def _read_bundled_example(name: str) -> str:
    example_name = _example_name(name)
    bundled = _bundled_examples()
    if example_name not in bundled:
        choices = ", ".join(sorted(Path(item).stem for item in bundled))
        hint = f" Available bundled examples: {choices}." if choices else ""
        raise typer.BadParameter(
            f"unknown bundled example '{name}'. Run `stui example list` to see names."
            f"{hint}"
        )
    return (
        resources.files("stui.examples")
        .joinpath(example_name)
        .read_text(encoding="utf-8")
    )


def _bundled_demo_resource(name: str):
    demo_name = _example_name(name)
    if Path(demo_name).stem not in DEMO_NAMES:
        choices = ", ".join(DEMO_NAMES)
        raise typer.BadParameter(
            f"unknown demo '{name}'. Run `stui demo list` to see names. "
            f"Available demos: {choices}."
        )

    try:
        demo_resource = resources.files("stui.examples").joinpath(demo_name)
    except ModuleNotFoundError as exc:
        raise typer.BadParameter(
            "bundled demo resources were not found in this installation."
        ) from exc

    if not demo_resource.is_file():
        raise typer.BadParameter(
            f"bundled demo '{Path(demo_name).stem}' was not found in this "
            "installation. Run `stui demo list` to see available demos."
        )
    return demo_resource


def _missing_script_message(script: Path) -> str:
    message = f"file does not exist: {script}"
    parts = script.parts
    if (
        len(parts) >= 2
        and parts[0] == "examples"
        and _example_name(parts[-1]) in _bundled_examples()
    ):
        stem = Path(parts[-1]).stem
        copy_dest = Path(*parts)
        message += (
            "\n\nBundled examples are available after installation, but they are "
            "not created in your current directory automatically. Run "
            f"`stui example copy {stem} {copy_dest}` first, then "
            f"`stui run {copy_dest}`."
        )
    return message


def _script_path_error(script: Path) -> str | None:
    if not script.exists():
        return _missing_script_message(script)
    if not script.is_file():
        return f"not a file: {script}"
    if script.suffix != ".py":
        return f"script must be a .py file: {script}"
    return None


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"stui {__version__}")
        raise typer.Exit()


def _bool_status(value: bool) -> str:
    return "yes" if value else "no"


def _color_capability(term: str, color_term: str) -> str:
    normalized_term = term.lower()
    normalized_color_term = color_term.lower()
    if not term or normalized_term == "dumb":
        return "none/dumb"
    if "truecolor" in normalized_color_term or "24bit" in normalized_color_term:
        return "truecolor"
    if "256color" in normalized_term:
        return "256-color"
    return "basic/unknown"


def _terminal_size_status(columns: int, lines: int) -> str:
    if columns < MIN_TERMINAL_COLUMNS or lines < MIN_TERMINAL_LINES:
        return (
            "small; recommended at least "
            f"{MIN_TERMINAL_COLUMNS}x{MIN_TERMINAL_LINES}"
        )
    return "ok"


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not installed"


def _distribution_location(name: str) -> str:
    try:
        return str(metadata.distribution(name).locate_file(""))
    except metadata.PackageNotFoundError:
        return "not installed"


def _doctor_diagnostics() -> dict[str, object]:
    terminal_size = shutil.get_terminal_size(fallback=(0, 0))
    example_infos = _example_infos()
    bundled_count = sum(info.bundled for info in example_infos)
    repo_count = sum(info.repo_path is not None for info in example_infos)
    term = os.environ.get("TERM", "")
    color_term = os.environ.get("COLORTERM", "")
    term_program = os.environ.get("TERM_PROGRAM", "")
    stui_theme = os.environ.get("STUI_THEME", "")
    no_color = os.environ.get("NO_COLOR", "")
    color_capability = _color_capability(term, color_term)
    size_status = _terminal_size_status(terminal_size.columns, terminal_size.lines)
    package_version = _package_version("stui-terminal")
    warnings = []
    if size_status != "ok":
        warnings.append(
            "terminal is too small; layout or chart rendering may be clipped"
        )
    if term.lower() == "dumb":
        warnings.append("TERM=dumb; interactive rendering and color may be limited")
    if package_version not in {"not installed", __version__}:
        warnings.append(
            "imported stui version and stui-terminal distribution version differ"
        )

    first_source = None
    if example_infos:
        first = example_infos[0]
        first_source = {
            "source": "bundled" if first.bundled else "repo-only",
            "location": "stui.examples" if first.bundled else str(first.repo_path),
        }

    return {
        "stui": __version__,
        "package": package_version,
        "python": {
            "version": sys.version.split()[0],
            "platform": platform.system(),
            "machine": platform.machine(),
        },
        "packages": {
            "textual": _package_version("textual"),
            "rich": _package_version("rich"),
            "typer": _package_version("typer"),
        },
        "locations": {
            "stui_import": str(Path(__file__).resolve().parents[1]),
            "distribution": _distribution_location("stui-terminal"),
        },
        "terminal": {
            "columns": terminal_size.columns,
            "lines": terminal_size.lines,
            "status": size_status,
            "minimum_columns": MIN_TERMINAL_COLUMNS,
            "minimum_lines": MIN_TERMINAL_LINES,
            "too_small": size_status != "ok",
        },
        "theme": resolve_theme(stui_theme),
        "environment": {
            "TERM": term,
            "COLORTERM": color_term,
            "TERM_PROGRAM": term_program,
            "STUI_THEME": stui_theme,
            "NO_COLOR": no_color,
        },
        "capabilities": {
            "color": color_capability,
            "stdin_tty": sys.stdin.isatty(),
            "stdout_tty": sys.stdout.isatty(),
            "stderr_tty": sys.stderr.isatty(),
            "unicode": sys.stdout.encoding or "unknown",
            "no_color_requested": bool(no_color),
        },
        "examples": {
            "bundled": bundled_count,
            "repo": repo_count,
            "first_source": first_source,
        },
        "warnings": warnings,
    }


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the stui version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Run tiny Streamlit-inspired terminal UI apps."""


@app.command()
def run(script: Path) -> None:
    """Run a Python stui script in the terminal."""

    script_path = script.expanduser()
    if error := _script_path_error(script_path):
        raise typer.BadParameter(error)

    runtime = Runtime(script_path.resolve())
    StuiApp(runtime).run()


@app.command("check")
def check_app(
    script: Path,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print validation result as JSON."),
    ] = False,
) -> None:
    """Validate a stui script without launching the interactive TUI."""

    script_path = script.expanduser()
    if error := _script_path_error(script_path):
        payload = _check_payload(
            script,
            script_path if script_path.is_absolute() else None,
            errors=[error],
            status="invalid_script",
            exit_code=2,
            error_kind=_script_error_kind(script_path, error),
            element_types={},
            element_count=0,
        )
        if json_output:
            typer.echo(json_module.dumps(payload, indent=2, sort_keys=True))
            raise typer.Exit(2)
        raise typer.BadParameter(error)

    runtime = Runtime(script_path.resolve())
    elements = runtime.run_script()
    errors = [
        element.traceback
        for element in elements
        if isinstance(element, ErrorElement)
    ]
    element_types = Counter(type(element).__name__ for element in elements)
    payload = _check_payload(
        script,
        script_path.resolve(),
        errors=errors,
        status="script_error" if errors else "ok",
        exit_code=1 if errors else 0,
        error_kind="script_error" if errors else None,
        element_types=dict(sorted(element_types.items())),
        element_count=len(elements),
    )

    if json_output:
        typer.echo(json_module.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        typer.echo(f"stui check failed: {script_path}")
        for error in errors:
            typer.echo(error)
    else:
        typer.echo(
            f"stui check passed: {script_path} "
            f"({len(elements)} rendered element{'s' if len(elements) != 1 else ''})"
        )

    if errors:
        raise typer.Exit(1)


def _script_error_kind(script: Path, message: str) -> str:
    if not script.exists():
        return "missing"
    if not script.is_file():
        return "not_file"
    if "must be a .py file" in message:
        return "not_python"
    return "invalid_script"


def _check_payload(
    input_script: Path,
    resolved_script: Path | None,
    *,
    errors: list[str],
    status: str,
    exit_code: int,
    error_kind: str | None,
    element_types: dict[str, int],
    element_count: int,
) -> dict[str, object]:
    error = None
    if errors:
        error = {
            "kind": error_kind or status,
            "message": errors[0].splitlines()[-1] if errors[0] else "",
            "traceback": errors[0],
        }
    return {
        "schema_version": "stui.check.v1",
        "stui_version": __version__,
        "ok": not errors,
        "status": status,
        "exit_code": exit_code,
        "script": {
            "input": str(input_script),
            "path": str(resolved_script) if resolved_script is not None else None,
        },
        "summary": {
            "element_count": element_count,
            "error_count": len(errors),
            "element_types": element_types,
        },
        "error": error,
    }


@app.command("demo")
def run_demo(name: str) -> None:
    """Run a bundled first-run demo directly from the installed package."""

    if name == "list":
        bundled = _bundled_examples()
        available = [
            demo_name
            for demo_name in DEMO_NAMES
            if _example_name(demo_name) in bundled
        ]
        typer.echo("stui demos:")
        if not available:
            typer.echo("  No bundled demos were found in this installation.")
            return
        for demo_name in available:
            description = EXAMPLE_DESCRIPTIONS.get(
                _example_name(demo_name),
                "Bundled demo app.",
            )
            typer.echo(f"  {demo_name} - {description}")
        return

    demo_resource = _bundled_demo_resource(name)
    with resources.as_file(demo_resource) as demo_path:
        runtime = Runtime(demo_path.resolve())
        StuiApp(runtime).run()


@app.command()
def doctor(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print diagnostics as JSON."),
    ] = False,
) -> None:
    """Print environment details useful for debugging stui installs."""

    diagnostics = _doctor_diagnostics()
    if json_output:
        typer.echo(json_module.dumps(diagnostics, indent=2, sort_keys=True))
        return

    python_info = diagnostics["python"]
    packages = diagnostics["packages"]
    terminal = diagnostics["terminal"]
    environment = diagnostics["environment"]
    capabilities = diagnostics["capabilities"]
    examples = diagnostics["examples"]

    typer.echo(f"stui: {diagnostics['stui']}")
    typer.echo(f"package: {diagnostics['package']}")
    typer.echo(
        f"python: {python_info['version']} "
        f"({python_info['platform']} {python_info['machine']})"
    )
    typer.echo(f"textual: {packages['textual']}")
    typer.echo(f"rich: {packages['rich']}")
    typer.echo(f"typer: {packages['typer']}")
    typer.echo(
        f"terminal size: {terminal['columns']}x{terminal['lines']} "
        f"({terminal['status']})"
    )
    typer.echo(f"theme: {diagnostics['theme']}")
    typer.echo(f"TERM: {environment['TERM'] or 'unknown'}")
    typer.echo(f"COLORTERM: {environment['COLORTERM'] or 'unknown'}")
    typer.echo(f"TERM_PROGRAM: {environment['TERM_PROGRAM'] or 'unknown'}")
    typer.echo(f"STUI_THEME: {environment['STUI_THEME'] or 'unset'}")
    typer.echo(f"NO_COLOR: {_bool_status(bool(environment['NO_COLOR']))}")
    typer.echo(
        "capabilities: "
        f"color={capabilities['color']}, "
        f"stdin_tty={_bool_status(bool(capabilities['stdin_tty']))}, "
        f"stdout_tty={_bool_status(bool(capabilities['stdout_tty']))}, "
        f"stderr_tty={_bool_status(bool(capabilities['stderr_tty']))}, "
        f"unicode={capabilities['unicode']}, "
        f"no_color_requested={_bool_status(bool(capabilities['no_color_requested']))}"
    )
    for warning in diagnostics["warnings"]:
        typer.echo(f"warning: {warning}.")
    typer.echo(
        f"examples: {examples['bundled']} bundled, {examples['repo']} repo"
    )
    first_source = examples["first_source"]
    if first_source:
        typer.echo(
            f"example source: {first_source['source']} "
            f"({first_source['location']})"
        )


@app.command("examples")
def list_examples() -> None:
    """List bundled and repository example app names with run/copy commands."""

    infos = _example_infos()
    if not infos:
        typer.echo("No bundled examples were found.")
        typer.echo("  https://github.com/marmar9615-cloud/stui-terminal/tree/main/examples")
        return

    typer.echo("stui examples:")
    for info in infos:
        stem = Path(info.name).stem
        description = EXAMPLE_DESCRIPTIONS.get(info.name, "Example app.")
        if info.bundled and info.repo_path is not None:
            source = f"bundled + repo ({info.repo_path})"
        elif info.bundled:
            source = "bundled"
        else:
            source = f"repo-only ({info.repo_path})"
        typer.echo(f"  {stem} - {description} [{source}]")
        if info.repo_path is not None:
            typer.echo(f"    repo run:     stui run {info.repo_path}")
        else:
            typer.echo(
                f"    bundled run:  stui example copy {stem} ./examples/{info.name} "
                f"&& stui run ./examples/{info.name}"
            )
        if info.bundled:
            typer.echo(
                f"    copy:         stui example copy {stem} "
                f"./examples/{info.name}"
            )


example_app = typer.Typer(add_completion=False, help="Work with bundled examples.")


@example_app.command("list")
def list_bundled_example_names() -> None:
    """List bundled example names that can be copied."""

    names = sorted(Path(name).stem for name in _bundled_examples())
    if not names:
        typer.echo("No bundled examples were found.")
        return
    for name in names:
        typer.echo(name)


@example_app.command("copy")
def copy_example(
    name: str,
    dest: Path,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite DEST if it already exists."),
    ] = False,
) -> None:
    """Copy a bundled example app to DEST."""

    example_name = _example_name(name)
    content = _read_bundled_example(name)
    dest_path = dest.expanduser()
    if dest_path.is_dir():
        dest_path = dest_path / example_name
        if dest_path.exists() and not force:
            raise typer.BadParameter(f"destination exists: {dest_path}")
    elif dest_path.suffix == "":
        dest_path.mkdir(parents=True, exist_ok=True)
        dest_path = dest_path / example_name
        if dest_path.exists() and not force:
            raise typer.BadParameter(f"destination exists: {dest_path}")
    elif dest_path.exists() and not force:
        raise typer.BadParameter(f"destination exists: {dest}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    typer.echo(f"Copied {example_name} to {dest_path}")


app.add_typer(example_app, name="example")


@app.command("init")
def init_app(
    script: Path,
    template: Annotated[
        str,
        typer.Option(
            "--template",
            "-t",
            help="Starter template to create: basic, dashboard, or forms.",
        ),
    ] = "basic",
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite APP.py if it already exists."),
    ] = False,
) -> None:
    """Create a small starter stui app."""

    script_path = script.expanduser()
    if script_path.exists() and script_path.is_dir():
        raise typer.BadParameter(f"not a file: {script}")
    if script_path.suffix != ".py":
        raise typer.BadParameter(f"script must be a .py file: {script}")
    if template not in INIT_TEMPLATES:
        choices = ", ".join(INIT_TEMPLATE_CHOICES)
        raise typer.BadParameter(
            f"unknown template '{template}'. Choose one of: {choices}"
        )
    if script_path.exists() and not force:
        raise typer.BadParameter(f"file exists: {script}")
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        INIT_TEMPLATES[template].format(filename=script_path.name),
        encoding="utf-8",
    )
    typer.echo(f"Created {script_path} from the {template} template")
