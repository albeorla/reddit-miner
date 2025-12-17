"""Ideas commands - top, show, export."""

from __future__ import annotations

import asyncio
import csv
import json
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from . import app, console
from ..config import get_settings
from ..store import AsyncStore


@app.command()
def top(
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of ideas to show.",
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db",
        help="Path to database file.",
    ),
):
    """Show top-scored ideas."""
    settings = get_settings()
    path = db_path or settings.db_path

    async def _top():
        store = AsyncStore(path)
        await store.connect()
        ideas = await store.get_top_ideas(limit=limit)
        await store.close()
        return ideas

    ideas = asyncio.run(_top())

    if not ideas:
        console.print("[yellow]No ideas found[/yellow]")
        return

    table = Table(title="Top 10 Ideas", show_header=True, header_style="bold")
    table.add_column("", width=2)
    table.add_column("Score", width=5)
    table.add_column("", width=2)
    table.add_column("$", width=3)
    table.add_column("", width=2)
    table.add_column("C", width=3)
    table.add_column("", width=2)
    table.add_column("Idea", width=45)
    table.add_column("Subreddit", width=10)

    for idea in ideas:
        summary = idea.get("idea_summary", "")
        table.add_row(
            "",
            str(idea.get("total_score", "-")),
            "",
            str(idea.get("profitability", "-")),
            "",
            str(idea.get("competition", "-")),
            "",
            (summary[:42] + "...") if len(summary) > 45 else summary,
            idea.get("subreddit", "")[:10],
        )

    console.print(table)
    console.print("\nP=Practicality, $=Profitability, D=Distribution, C=Competition, M=Moat")


@app.command()
def show(
    idea_id: int = typer.Argument(..., help="Idea ID to show details for."),
    db_path: Optional[str] = typer.Option(
        None,
        "--db",
        help="Path to database file.",
    ),
):
    """Show detailed information about a specific idea."""
    settings = get_settings()
    path = db_path or settings.db_path

    async def _show():
        store = AsyncStore(path)
        await store.connect()
        idea = await store.get_idea_detail(idea_id)
        await store.close()
        return idea

    idea = asyncio.run(_show())

    if not idea:
        console.print(f"[red]Idea {idea_id} not found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Idea #{idea_id}[/bold]")
    console.print("─" * 60)

    console.print(f"\n[bold]Summary:[/bold] {idea.get('idea_summary', 'N/A')}")
    console.print(f"[bold]Subreddit:[/bold] r/{idea.get('subreddit', 'N/A')}")
    console.print(f"[bold]Post:[/bold] {idea.get('post_title', 'N/A')}")
    console.print(f"[bold]Link:[/bold] {idea.get('permalink', 'N/A')}")

    console.print(f"\n[bold]Score:[/bold] {idea.get('total_score', 0)}/50")
    if idea.get("disqualified"):
        console.print("[red]⚠ DISQUALIFIED[/red]")

    console.print("\n[bold]Dimensions:[/bold]")
    console.print(f"  Practicality:  {idea.get('practicality', '-')}/10")
    console.print(f"  Profitability: {idea.get('profitability', '-')}/10")
    console.print(f"  Distribution:  {idea.get('distribution', '-')}/10")
    console.print(f"  Competition:   {idea.get('competition', '-')}/10")
    console.print(f"  Moat:          {idea.get('moat', '-')}/10")

    console.print(f"\n[bold]Target User:[/bold] {idea.get('target_user', 'N/A')}")
    console.print(f"[bold]Pain Point:[/bold] {idea.get('pain_point', 'N/A')}")
    console.print(f"[bold]Solution:[/bold] {idea.get('proposed_solution', 'N/A')}")

    # Evidence
    evidence = idea.get("evidence_signals")
    if evidence:
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except json.JSONDecodeError:
                evidence = []
        if evidence:
            console.print("\n[bold]Evidence:[/bold]")
            for e in evidence:
                console.print(f"  • {e}")

    # Validation steps
    steps = idea.get("next_validation_steps")
    if steps:
        if isinstance(steps, str):
            try:
                steps = json.loads(steps)
            except json.JSONDecodeError:
                steps = []
        if steps:
            console.print("\n[bold]Validation Steps:[/bold]")
            for step in steps:
                console.print(f"  • {step}")

    # Reasoning
    why = idea.get("why")
    if why:
        if isinstance(why, str):
            try:
                why = json.loads(why)
            except json.JSONDecodeError:
                why = []
        if why:
            console.print("\n[bold]Reasoning:[/bold]")
            for w in why:
                console.print(f"  • {w}")


@app.command()
def export(
    output: str = typer.Option(
        "ideas.json",
        "--output",
        "-o",
        help="Output file path (.json or .csv).",
    ),
    limit: int = typer.Option(
        50,
        "--limit",
        "-l",
        help="Number of ideas to export.",
    ),
    include_disqualified: bool = typer.Option(
        False,
        "--include-disqualified",
        help="Include disqualified ideas.",
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db",
        help="Path to database file.",
    ),
):
    """Export top ideas to JSON or CSV."""
    settings = get_settings()
    path = db_path or settings.db_path

    async def _export():
        store = AsyncStore(path)
        await store.connect()
        ideas = await store.get_top_ideas(limit=limit, include_disqualified=include_disqualified)
        await store.close()
        return ideas

    ideas = asyncio.run(_export())

    if not ideas:
        console.print("[yellow]No ideas to export[/yellow]")
        return

    output_path = Path(output)

    if output.endswith(".csv"):
        with open(output_path, "w", newline="") as f:
            if ideas:
                writer = csv.DictWriter(f, fieldnames=ideas[0].keys())
                writer.writeheader()
                writer.writerows(ideas)
    else:
        with open(output_path, "w") as f:
            json.dump(ideas, f, indent=2, default=str)

    console.print(f"[green]✓ Exported {len(ideas)} ideas to {output}[/green]")
