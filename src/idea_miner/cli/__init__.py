"""CLI subpackage for Idea Miner.

Provides a modular CLI structure with commands organized by function.
"""

from __future__ import annotations

import typer
from rich.console import Console

from ..config import Settings, get_settings
from ..logging_config import configure_logging, get_logger

# Create main app
app = typer.Typer(
    name="idea-miner",
    help="Mine Reddit for microSaaS and side-hustle ideas using AI.",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        from .. import __version__

        console.print(f"idea-miner {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Idea Miner - Mine Reddit for microSaaS ideas."""
    pass


# Import and register command modules
from . import fetch, ideas, pipeline, report, db  # noqa: E402, F401
