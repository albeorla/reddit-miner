import pytest
from unittest.mock import MagicMock, AsyncMock
from langchain_core.language_models import BaseChatModel
from src.pain_radar.models import FullAnalysis, Extraction, Score, ExtractionState, Cluster, ClusterItem, EvidenceSignal, EvidenceType

@pytest.fixture
def mock_llm():
    """Mock LangChain Chat Model."""
    llm = MagicMock(spec=BaseChatModel)
    llm.with_structured_output.return_value = llm  # Allow chaining
    llm.ainvoke = AsyncMock()
    return llm

@pytest.fixture
def sample_post():
    """Sample RedditPost for testing."""
    from src.pain_radar.reddit_async import RedditPost
    return RedditPost(
        id="test_id",
        title="Test Title",
        body="Test Body",
        url="http://test.url",
        author="test_author",
        subreddit="test_subreddit",
        created_utc=1234567890.0,
        score=10,
        num_comments=5,
        top_comments=["Comment 1", "Comment 2"]
    )

@pytest.fixture
def sample_full_analysis_extracted():
    """Sample FullAnalysis result (EXTRACTED)."""
    return FullAnalysis(
        extraction=Extraction(
            extraction_state=ExtractionState.EXTRACTED,
            pain_point="Cannot find X",
            signal_summary="User struggles to find X",
            evidence_strength="high",
            extracted_quotes=["I can't find X"],
            risk_flags=[]
        ),
        score=Score(
            total=85,
            pain_level=8,
            commercial_intent=7,
            specificity=9,
            comment_quality=8,
            confidence="high"
        )
    )

@pytest.fixture
def sample_cluster_item():
    return ClusterItem(
        id="item1",
        summary="Summary 1",
        pain_point="Pain 1",
        subreddit="sub1",
        evidence=[
            EvidenceSignal(
                quote="Quote 1",
                signal_type="pain", 
                evidence_type=EvidenceType.POST_BODY
            )
        ]
    )
