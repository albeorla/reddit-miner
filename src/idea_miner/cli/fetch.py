"""Fetch command - fetch posts from Reddit without AI processing."""

from __future__ import annotations

import asyncio
from typing import List, Optional

import typer

from . import app, console
from ..config import get_settings
from ..logging_config import configure_logging
from ..pipeline import run_fetch_only


@app.command()
def fetch(
    subreddits: Optional[List[str]] = typer.Option(
        None,
        "--subreddit",
        "-s",
        help="Subreddits to fetch (can specify multiple).",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum posts per subreddit.",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging level.",
    ),
):
    """Fetch posts from Reddit without AI processing.

    Useful for building up a corpus before running AI analysis.
    """
    configure_logging(log_level, False)

    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        raise typer.Exit(1)

    # Apply overrides
    if subreddits:
        settings.subreddits = list(subreddits)
    if limit:
        settings.posts_per_subreddit = limit

    console.print(f"\nFetching posts from {len(settings.subreddits)} subreddits...")

    try:
        result = asyncio.run(run_fetch_only(settings))
        console.print(f"[green]✓ Fetched {result} posts[/green]")
    except Exception as e:
        console.print(f"[red]Fetch failed:[/red] {e}")
        raise typer.Exit(1)
