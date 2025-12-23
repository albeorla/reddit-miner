from datetime import UTC, datetime, timedelta

import httpx
import pytest

from pain_radar.http_client import create_http_client, parse_retry_after


def test_parse_retry_after():
    """Test parsing Retry-After header."""
    # Integer
    resp = httpx.Response(429, headers={"Retry-After": "30"})
    assert parse_retry_after(resp) == 30.0

    # Date (future)
    future_date = (datetime.now(UTC) + timedelta(seconds=60)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    resp = httpx.Response(429, headers={"Retry-After": future_date})
    val = parse_retry_after(resp)
    assert val > 50.0 and val <= 60.0

    # Missing
    resp = httpx.Response(429)
    assert parse_retry_after(resp) is None


@pytest.mark.asyncio
async def test_create_http_client():
    """Test HTTP client creation."""
    async with create_http_client(user_agent="test") as client:
        assert isinstance(client, httpx.AsyncClient)
        # Check User-Agent (case sensitivity might vary, httpx usually normalizes)
        ua = client.headers.get("user-agent") or client.headers.get("User-Agent")
        assert ua == "test"
