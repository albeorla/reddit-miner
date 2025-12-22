import pytest
import aiosqlite
import os
from pain_radar.store.core import AsyncStore

@pytest.mark.asyncio
async def test_async_store_connect_and_init():
    """Test that we can connect to the database and initialize the schema."""
    db_path = ":memory:" # Use in-memory for testing
    store = AsyncStore(db_path)
    
    # Verify not connected initially
    assert store._connection is None
    
    # Connect
    await store.connect()
    assert store._connection is not None
    
    # Init DB
    await store.init_db()
    
    # Verify tables exist by querying sqlite_master
    async with store.connection() as conn:
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in await cursor.fetchall()]
        assert "posts" in tables
        assert "signals" in tables
        assert "runs" in tables
        assert "clusters" in tables
        assert "watchlists" in tables
        assert "source_sets" in tables
        assert "alert_matches" in tables

    # Close connection
    await store.close()
    assert store._connection is None

@pytest.mark.asyncio
async def test_async_store_connection_context_manager():
    """Test that the connection context manager works as expected."""
    db_path = ":memory:"
    store = AsyncStore(db_path)
    
    async with store.connection() as conn:
        assert store._connection is not None
        assert isinstance(conn, aiosqlite.Connection)
        
    # Connection should still be open after context manager if not closed explicitly
    # (Actually AsyncStore's connection method doesn't close it, it just ensures it's open)
    assert store._connection is not None
    await store.close()
