import pytest
import aiosqlite
import os
import json
from pain_radar.store.core import AsyncStore
from pain_radar.models import FullAnalysis, ExtractionState, PainSignal, SignalScore, DistributionWedge, ExtractionType, CompetitorNote
from pain_radar.reddit_async import RedditPost

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
        
    assert store._connection is not None
    await store.close()

@pytest.mark.asyncio
async def test_async_store_signal_crud(sample_post, sample_full_analysis_extracted):
    """Test CRUD operations for Signals."""
    db_path = ":memory:"
    store = AsyncStore(db_path)
    await store.init_db()
    
    # 1. Upsert Post (Foreign key dependency)
    await store.upsert_posts([sample_post])
    
    # 2. Save Signal
    signal_id = await store.save_signal(
        post=sample_post,
        extraction=sample_full_analysis_extracted.extraction,
        score=sample_full_analysis_extracted.score
    )
    assert signal_id > 0
    
    # 3. Get Signal Detail
    detail = await store.get_signal_detail(signal_id)
    assert detail is not None
    assert detail["post_id"] == sample_post.id
    assert detail["signal_summary"] == sample_full_analysis_extracted.extraction.signal_summary
    assert detail["total_score"] == sample_full_analysis_extracted.score.total
    
    # 4. Get Top Signals
    top = await store.get_top_signals(limit=10)
    assert len(top) == 1
    assert top[0]["id"] == signal_id
    
    # 5. Get Stats
    stats = await store.get_stats()
    assert stats["total_posts"] == 1
    assert stats["total_signals"] == 1
    assert stats["qualified_signals"] == 1
    
    await store.close()

@pytest.mark.asyncio
async def test_async_store_disqualified_signal(sample_post):
    """Test saving a disqualified signal."""
    db_path = ":memory:"
    store = AsyncStore(db_path)
    await store.init_db()
    await store.upsert_posts([sample_post])
    
    extraction = PainSignal(
        extraction_state=ExtractionState.DISQUALIFIED,
        extraction_type=ExtractionType.IDEA,
        signal_summary="Self-promotion",
        risk_flags=["self_promo"],
        evidence=[],
    )
    
    signal_id = await store.save_signal(post=sample_post, extraction=extraction)
    
    detail = await store.get_signal_detail(signal_id)
    assert detail["disqualified"] == 0 # Wait, AsyncStore.save_signal sets disqualified from score.disqualified
    # If score is None, it sets disqualified = 0.
    
    # Let's check save_signal implementation for disqualified state when score is missing but extraction is DISQUALIFIED
    # In core.py:
    # if score:
    #     disqualified = 1 if score.disqualified else 0
    # else:
    #     disqualified = 0
    
    # So if we want it disqualified, we MUST provide a score with disqualified=True
    
    score = SignalScore(
        disqualified=True,
        disqualify_reasons=["Self-promotion"],
        practicality=0, profitability=0, distribution=0, competition=0, moat=0,
        confidence=1.0,
        distribution_wedge=DistributionWedge.COMMUNITY,
        distribution_wedge_detail="N/A",
        competition_landscape=[CompetitorNote(category="N/A", your_wedge="N/A")]
    )
    
    signal_id_2 = await store.save_signal(post=sample_post, extraction=extraction, score=score)
    detail_2 = await store.get_signal_detail(signal_id_2)
    assert detail_2["disqualified"] == 1
    
    await store.close()