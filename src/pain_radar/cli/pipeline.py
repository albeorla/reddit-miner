"""Pipeline command - run the full mining pipeline."""

from __future__ import annotations

import asyncio
from typing import List, Optional

import typer
from langchain_openai import ChatOpenAI
from rich.table import Table

from . import app, console
from ..config import get_settings
from ..logging_config import configure_logging, get_logger
from ..pipeline import run_pipeline, run_process_only
from ..progress import create_progress, set_progress


@app.command()
def run(
    subreddits: Optional[List[str]] = typer.Option(
        None,
        "--subreddit",
        "-s",
        help="Subreddits to mine (can specify multiple). Overrides config.",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum posts per subreddit to fetch.",
    ),
    process_limit: Optional[int] = typer.Option(
        None,
        "--process-limit",
        "-p",
        help="Maximum posts to process with AI.",
    ),
    skip_fetch: bool = typer.Option(
        False,
        "--skip-fetch",
        help="Skip fetching new posts, only process existing unprocessed posts.",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging level: DEBUG, INFO, WARNING, ERROR",
    ),
    log_json: bool = typer.Option(
        False,
        "--log-json",
        help="Output logs as JSON.",
    ),
    no_progress: bool = typer.Option(
        False,
        "--no-progress",
        help="Disable progress bars (useful for logging).",
    ),
):
    """Run the full pain signal pipeline.

    Fetches posts from Reddit, analyzes them with AI, and stores the results.
    """
    configure_logging(log_level, log_json)
    logger = get_logger(__name__)

    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("\nMake sure you have a .env file with:")
        console.print("  OPENAI_API_KEY=sk-...")
        raise typer.Exit(1)

    # Apply CLI overrides
    if subreddits:
        settings.subreddits = list(subreddits)
    if limit:
        settings.posts_per_subreddit = limit

    # Create LLM
    if not settings.openai_api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY not set")
        raise typer.Exit(1)

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    console.print(f"\n[bold]Pain Radar[/bold] - Scanning {len(settings.subreddits)} subreddits")
    console.print(f"  Subreddits: {', '.join(settings.subreddits)}")
    console.print(f"  Posts per subreddit: {settings.posts_per_subreddit}")
    console.print(f"  Model: {settings.openai_model}")
    console.print()

    async def _run():
        if skip_fetch:
            return await run_process_only(settings, llm, process_limit)
        else:
            return await run_pipeline(settings, llm, fetch_new=True, process_limit=process_limit)

    try:
        # Use progress bars unless disabled or logging JSON
        if no_progress or log_json:
            result = asyncio.run(_run())
        else:
            # Run with progress display
            progress = create_progress()
            with progress:
                set_progress(progress)
                result = asyncio.run(_run())
                set_progress(None)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        logger.exception("pipeline_failed")
        console.print(f"\n[red]Pipeline failed:[/red] {e}")
        raise typer.Exit(1)

    # Display results
    console.print(f"\n[green]✓ Pipeline complete[/green] (Run #{result.run_id})")
    console.print(f"  Posts fetched: {result.posts_fetched}")
    console.print(f"  Posts analyzed: {result.posts_analyzed}")
    console.print(f"  Signals saved: {result.ideas_saved}")
    console.print(f"  Qualified: {result.qualified_ideas}")
    console.print(f"  Errors: {result.errors}")

    if result.top_ideas:
        console.print("\n[bold]Top Ideas:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Score", width=6)
        table.add_column("Idea", width=50)
        table.add_column("Subreddit", width=15)

        for sig in result.top_ideas[:5]:
            summary = idea.get("signal_summary", "")
            table.add_row(
                str(idea.get("total_score", "-")),
                (summary[:47] + "...") if len(summary) > 50 else summary,
                idea.get("subreddit", ""),
            )
        console.print(table)
