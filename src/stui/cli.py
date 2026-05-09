from __future__ import annotations

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
