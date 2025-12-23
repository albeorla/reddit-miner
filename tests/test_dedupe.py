from pain_radar.dedupe import combined_similarity, dedupe_ideas, similarity_ratio
from pain_radar.models import ExtractionState, PainSignal


def test_similarity_ratio():
    """Test string similarity ratio."""
    assert similarity_ratio("Hello World", "world hello") == 1.0
    assert similarity_ratio("Python", "Java") < 0.5


def test_combined_similarity():
    """Test combined similarity across fields."""
    s1 = PainSignal(
        extraction_state=ExtractionState.EXTRACTED,
        signal_summary="Stripe for creators",
        pain_point="Payments are hard",
        target_user="Creators",
    )
    s2 = PainSignal(
        extraction_state=ExtractionState.EXTRACTED,
        signal_summary="Payments for creators via Stripe",
        pain_point="Payments are hard",
        target_user="Creators",
    )
    sim = combined_similarity(s1, s2)
    assert sim > 0.8


def test_dedupe_ideas():
    """Test deduplicating a list of ideas."""
    s1 = PainSignal(
        extraction_state=ExtractionState.EXTRACTED,
        signal_summary="Stripe for creators",
        pain_point="Payments are hard",
        target_user="Creators",
    )
    s2 = PainSignal(
        extraction_state=ExtractionState.EXTRACTED,
        signal_summary="Payments for creators",
        pain_point="Payments are difficult",
        target_user="Creators",
    )
    s3 = PainSignal(
        extraction_state=ExtractionState.EXTRACTED,
        signal_summary="Different idea entirely",
        pain_point="Different pain",
        target_user="Different user",
    )

    ideas = [("p1", s1), ("p2", s2), ("p3", s3)]
    results = dedupe_ideas(ideas, similarity_threshold=0.7)

    assert len(results) == 2  # s1 and s2 should be deduped
    assert results[0][0] == "p1"
    assert "p2" in results[0][2]  # p2 is a duplicate of p1
    assert results[1][0] == "p3"
