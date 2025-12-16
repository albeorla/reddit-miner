"""Typer CLI for Idea Miner.

This module re-exports from the cli subpackage for backward compatibility.
The actual commands are defined in cli/*.py
"""

from .cli import app, console

__all__ = ["app", "console"]
