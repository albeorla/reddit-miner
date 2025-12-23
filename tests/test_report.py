import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock
from pain_radar.report import generate_report, generate_json_report

@pytest.mark.asyncio
async def test_generate_report(tmp_path):
    """Test generating a markdown report."""
    mock_store = MagicMock()
    mock_store.get_run = AsyncMock(return_value={
        "id": 1,
        "started_at": "2023-01-01T00:00:00",
        "subreddits": '["test"]',
        "posts_fetched": 10,
        "posts_analyzed": 5
    })
    mock_store.get_signals_for_run = AsyncMock(return_value=[
        {"id": 1, "signal_summary": "Test signal", "total_score": 40, "disqualified": False}
    ])
    mock_store.get_stats = AsyncMock(return_value={"avg_score": 40})
    
    output_dir = tmp_path / "reports"
    report_path = await generate_report(mock_store, run_id=1, output_dir=str(output_dir))
    
    assert os.path.exists(report_path)
    with open(report_path, "r") as f:
        content = f.read()
        assert "# Pain Radar Report - Run #1" in content
        assert "Test signal" in content

@pytest.mark.asyncio
async def test_generate_json_report(tmp_path):
    """Test generating a JSON report."""
    mock_store = MagicMock()
    mock_store.get_runs = AsyncMock(return_value=[{"id": 1}])
    mock_store.get_signals_for_run = AsyncMock(return_value=[
        {"id": 1, "signal_summary": "Test signal", "total_score": 40, "disqualified": False}
    ])
    mock_store.get_stats = AsyncMock(return_value={"avg_score": 40})
    
    output_dir = tmp_path / "reports"
    report_path = await generate_json_report(mock_store, run_id=None, output_dir=str(output_dir))
    
    assert os.path.exists(report_path)
    with open(report_path, "r") as f:
        data = json.load(f)
        assert data["run"]["id"] == 1
        assert data["ideas"][0]["signal_summary"] == "Test signal"
