from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from pain_radar.api.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_list_signals():
    """Test listing signals via API."""
    with patch("pain_radar.api.v1.endpoints.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_top_signals = AsyncMock(return_value=[{"id": 1, "summary": "test"}])

        response = client.get("/v1/signals")

        assert response.status_code == 200
        data = response.json()

        # Correct assertion
        assert len(data) == 1
        assert data[0]["summary"] == "test"


@pytest.mark.asyncio
async def test_get_signal_found():
    """Test getting a specific signal."""
    with patch("pain_radar.api.v1.endpoints.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_signal_detail = AsyncMock(return_value={"id": 1, "summary": "test"})

        response = client.get("/v1/signals/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_signal_not_found():
    """Test getting a non-existent signal."""
    with patch("pain_radar.api.v1.endpoints.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_signal_detail = AsyncMock(return_value=None)

        response = client.get("/v1/signals/999")

        assert response.status_code == 404
