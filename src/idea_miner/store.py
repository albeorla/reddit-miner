"""Async SQLite storage layer.

This module re-exports from the store subpackage for backward compatibility.
"""

from .store import AsyncStore

__all__ = ["AsyncStore"]
