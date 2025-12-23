from fastapi import APIRouter, Depends, HTTPException
from ...store import AsyncStore
from ...config import get_settings

router = APIRouter()
settings = get_settings()

async def get_store():
    store = AsyncStore(settings.db_path)
    await store.connect()
    try:
        yield store
    finally:
        await store.close()

@router.get("/signals", response_model=list[dict])
async def list_signals(limit: int = 10, store: AsyncStore = Depends(get_store)):
    """List recent pain signals."""
    signals = await store.get_top_signals(limit=limit)
    return signals

@router.get("/signals/{signal_id}", response_model=dict)
async def get_signal(signal_id: int, store: AsyncStore = Depends(get_store)):
    """Get a specific signal."""
    signal = await store.get_signal_detail(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal
