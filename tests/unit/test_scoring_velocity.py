"""Unit tests for Velocity Detector scoring module."""

import pytest
from fraud_detection.scoring.velocity import VelocityDetector
from fraud_detection.services.enrichment import EnrichedContext


@pytest.fixture
def detector():
    return VelocityDetector()


class TestVelocityDetector:
    async def test_normal_velocity(self, detector, make_scoring_context, sample_enriched_context):
        """Normal velocity should score 0."""
        sample_enriched_context.velocity_1m = 1
        sample_enriched_context.velocity_5m = 3
        sample_enriched_context.velocity_1h = 8
        sample_enriched_context.velocity_24h = 20
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await detector.score(context)
        assert result.score == 0

    async def test_burst_1m(self, detector, make_scoring_context, sample_enriched_context):
        """3+ txns in 1 minute should trigger burst detection."""
        sample_enriched_context.velocity_1m = 5
        sample_enriched_context.velocity_5m = 6
        sample_enriched_context.velocity_1h = 10
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await detector.score(context)
        assert result.score > 0
        assert any("1 minute" in s for s in result.signals)

    async def test_severe_burst(self, detector, make_scoring_context, sample_enriched_context):
        """12+ txns in 1 minute should score very high."""
        sample_enriched_context.velocity_1m = 12
        sample_enriched_context.velocity_5m = 15
        sample_enriched_context.velocity_1h = 20
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await detector.score(context)
        assert result.score >= 50

    async def test_5m_burst(self, detector, make_scoring_context, sample_enriched_context):
        """8+ txns in 5 minutes should trigger."""
        sample_enriched_context.velocity_1m = 2
        sample_enriched_context.velocity_5m = 10
        sample_enriched_context.velocity_1h = 12
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await detector.score(context)
        assert result.score > 0
        assert any("5 minutes" in s for s in result.signals)

    async def test_high_daily_volume(self, detector, make_scoring_context, sample_enriched_context):
        """50+ txns in 24h should trigger."""
        sample_enriched_context.velocity_1m = 1
        sample_enriched_context.velocity_5m = 3
        sample_enriched_context.velocity_1h = 10
        sample_enriched_context.velocity_24h = 55
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await detector.score(context)
        assert any("24h" in s for s in result.signals)

    async def test_confidence_high(self, detector, make_scoring_context):
        """Velocity detector should have high confidence."""
        context = make_scoring_context()
        result = await detector.score(context)
        assert result.confidence >= 0.9
