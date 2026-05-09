from __future__ import annotations

import os
import platform
import shutil
import sys
from importlib import metadata
from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .app import StuiApp
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
    "kitchen_sink.py",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"stui {__version__}")
        raise typer.Exit()


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

    columns = shutil.get_terminal_size(fallback=(0, 0)).columns
    typer.echo(f"stui: {__version__}")
    typer.echo(
        f"python: {sys.version.split()[0]} "
        f"({platform.system()} {platform.machine()})"
    )
    typer.echo(f"textual: {package_version('textual')}")
    typer.echo(f"rich: {package_version('rich')}")
    typer.echo(f"typer: {package_version('typer')}")
    typer.echo(f"terminal columns: {columns}")
    typer.echo(f"TERM: {os.environ.get('TERM', 'unknown')}")


@app.command("examples")
def list_examples() -> None:
    """List bundled example app names and run commands."""

    examples_dir = Path(__file__).resolve().parents[2] / "examples"
    typer.echo("Bundled examples:")
    for name in EXAMPLE_NAMES:
        path = examples_dir / name
        suffix = f" ({path})" if path.exists() else ""
        typer.echo(f"  stui run examples/{name}{suffix}")
