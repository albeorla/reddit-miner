import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock
from pain_radar.cli import app

runner = CliRunner()

@pytest.fixture
def mock_settings():
    with patch("pain_radar.cli.db.get_settings") as m1, \
         patch("pain_radar.cli.report.get_settings") as m2, \
         patch("pain_radar.cli.ideas.get_settings") as m3, \
         patch("pain_radar.cli.cluster.get_settings") as m4, \
         patch("pain_radar.cli.alerts.get_settings") as m5:
        settings = MagicMock()
        settings.db_path = ":memory:"
        m1.return_value = settings
        m2.return_value = settings
        m3.return_value = settings
        m4.return_value = settings
        m5.return_value = settings
        yield settings

def test_db_stats(mock_settings):
    """Test db stats command."""
    with patch("pain_radar.cli.db.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_stats = AsyncMock(return_value={"total_posts": 10})
        
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Total Posts" in result.stdout

def test_ideas_top(mock_settings):
    """Test top signals command."""
    with patch("pain_radar.cli.ideas.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_top_signals = AsyncMock(return_value=[{"signal_summary": "Top Signal", "total_score": 45}])
        
        result = runner.invoke(app, ["top"])
        assert result.exit_code == 0
        assert "Top Signal" in result.stdout

def test_report_runs(mock_settings):
    """Test report runs command."""
    with patch("pain_radar.cli.report.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_runs = AsyncMock(return_value=[{"id": 123, "status": "completed"}])
        
        result = runner.invoke(app, ["runs"])
        assert result.exit_code == 0
        assert "Pipeline Runs" in result.stdout
        assert "123" in result.stdout
        # Rich might truncate status
        assert "complet" in result.stdout

def test_cluster_command(mock_settings):
    """Test cluster command."""
    with patch("pain_radar.cli.cluster.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_unclustered_pain_points = AsyncMock(return_value=[{"id": 1, "summary": "test"}])
        
        with patch("pain_radar.cli.cluster.Clusterer") as mock_clusterer_cls:
            mock_clusterer = mock_clusterer_cls.return_value
            cluster = MagicMock()
            cluster.title = "Cluster Title"
            cluster.signal_ids = [1]
            cluster.summary = "Cluster Summary"
            cluster.target_audience = "Audience"
            cluster.why_it_matters = "Why"
            mock_clusterer.cluster_items = AsyncMock(return_value=[cluster])
            
            result = runner.invoke(app, ["cluster", "--dry-run"])
            assert result.exit_code == 0
            assert "Cluster Title" in result.stdout

def test_alerts_list(mock_settings):
    """Test alerts list command."""
    with patch("pain_radar.cli.alerts.AsyncStore") as mock_store_cls:
        mock_store = mock_store_cls.return_value
        mock_store.connect = AsyncMock()
        mock_store.close = AsyncMock()
        mock_store.get_watchlists = AsyncMock(return_value=[{
            "id": 1, 
            "name": "My Watchlist", 
            "keywords": ["stripe"], 
            "subreddits": [], 
            "total_matches": 0, 
            "is_active": True
        }])
        
        result = runner.invoke(app, ["alerts"])
        assert result.exit_code == 0
        assert "stripe" in result.stdout
        assert "My Watchlist" in result.stdout
