from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass
from importlib import metadata, resources
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .app import StuiApp, resolve_theme
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
    if not script_path.exists():
        raise typer.BadParameter(f"file does not exist: {script}")
    if not script_path.is_file():
        raise typer.BadParameter(f"not a file: {script}")
    if script_path.suffix != ".py":
        raise typer.BadParameter(f"script must be a .py file: {script}")

    runtime = Runtime(script_path.resolve())
    StuiApp(runtime).run()


@app.command()
def doctor() -> None:
    """Print environment details useful for debugging stui installs."""

    def package_version(name: str) -> str:
        try:
            return metadata.version(name)
        except metadata.PackageNotFoundError:
            return "not installed"

    terminal_size = shutil.get_terminal_size(fallback=(0, 0))
    example_infos = _example_infos()
    bundled_count = sum(info.bundled for info in example_infos)
    repo_count = sum(info.repo_path is not None for info in example_infos)
    term = os.environ.get("TERM", "")
    color_term = os.environ.get("COLORTERM", "")
    term_program = os.environ.get("TERM_PROGRAM", "")
    color_capability = _color_capability(term, color_term)
    capabilities = [
        f"color={color_capability}",
        f"stdin_tty={_bool_status(sys.stdin.isatty())}",
        f"stdout_tty={_bool_status(sys.stdout.isatty())}",
        f"stderr_tty={_bool_status(sys.stderr.isatty())}",
        f"unicode={sys.stdout.encoding or 'unknown'}",
    ]
    typer.echo(f"stui: {__version__}")
    typer.echo(f"package: {package_version('stui-terminal')}")
    typer.echo(
        f"python: {sys.version.split()[0]} "
        f"({platform.system()} {platform.machine()})"
    )
    typer.echo(f"textual: {package_version('textual')}")
    typer.echo(f"rich: {package_version('rich')}")
    typer.echo(f"typer: {package_version('typer')}")
    size_status = _terminal_size_status(terminal_size.columns, terminal_size.lines)
    typer.echo(
        f"terminal size: {terminal_size.columns}x{terminal_size.lines} "
        f"({size_status})"
    )
    typer.echo(f"theme: {resolve_theme()}")
    typer.echo(f"TERM: {term or 'unknown'}")
    typer.echo(f"COLORTERM: {color_term or 'unknown'}")
    typer.echo(f"TERM_PROGRAM: {term_program or 'unknown'}")
    typer.echo(f"capabilities: {', '.join(capabilities)}")
    if size_status != "ok":
        typer.echo(
            "warning: terminal is smaller than the recommended minimum; "
            "layout or chart rendering may be clipped."
        )
    typer.echo(
        f"examples: {bundled_count} bundled, {repo_count} repo"
    )
    if example_infos:
        first = example_infos[0]
        source = "bundled" if first.bundled else "repo-only"
        location = "stui.examples" if first.bundled else str(first.repo_path)
        typer.echo(f"example source: {source} ({location})")


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
