import asyncio

import httpx
import pytest
from pain_radar.retry_policy import RateLimitError, TransientHTTPError, adaptive_sleep, check_response_for_retry


def test_check_response_for_retry():
    """Test response checking for retries."""
    request = httpx.Request("GET", "https://example.com")

    # 429
    resp_429 = httpx.Response(429, headers={"Retry-After": "10"}, request=request)
    with pytest.raises(RateLimitError) as exc:
        check_response_for_retry(resp_429)
    assert exc.value.status_code == 429
    assert exc.value.retry_after == 10.0

    # 500
    resp_500 = httpx.Response(500, request=request)
    with pytest.raises(TransientHTTPError):
        check_response_for_retry(resp_500)

    # 200
    resp_200 = httpx.Response(200, request=request)
    check_response_for_retry(resp_200)  # Should not raise

    # 404
    resp_404 = httpx.Response(404, request=request)
    with pytest.raises(httpx.HTTPStatusError):
        check_response_for_retry(resp_404)


@pytest.mark.asyncio
async def test_adaptive_sleep(monkeypatch):
    """Test adaptive sleep logic."""
    sleep_calls = []

    async def mock_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    await adaptive_sleep(10.0)
    assert sleep_calls == [10.0]

    sleep_calls.clear()
    await adaptive_sleep(None, default=2.0)
    assert sleep_calls == [2.0]

    sleep_calls.clear()
    await adaptive_sleep(100.0)  # Cap at 60
    assert sleep_calls == [60.0]
