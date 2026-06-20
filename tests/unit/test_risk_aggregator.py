"""Unit tests for Risk Aggregator."""

import pytest
from fraud_detection.scoring.base import ScoringResult
from fraud_detection.services.risk_aggregator import RiskAggregator, WEIGHTS


@pytest.fixture
def aggregator():
    return RiskAggregator()


class TestRiskAggregator:
    def test_all_zeros(self, aggregator):
        """All zero scores should produce zero aggregate."""
        scores = {name: ScoringResult(score=0, confidence=0.9) for name in WEIGHTS}
        result = aggregator.aggregate(scores)
        assert result.total_score == 0.0

    def test_all_max(self, aggregator):
        """All 100 scores should produce 100 aggregate."""
        scores = {name: ScoringResult(score=100, confidence=1.0) for name in WEIGHTS}
        result = aggregator.aggregate(scores)
        assert result.total_score == 100.0

    def test_weighted_calculation(self, aggregator):
        """Verify correct weight application."""
        scores = {
            "behavior_analyzer": ScoringResult(score=40, confidence=0.8),
            "velocity_detector": ScoringResult(score=60, confidence=0.9),
            "device_risk": ScoringResult(score=80, confidence=0.85),
            "merchant_risk": ScoringResult(score=20, confidence=0.7),
            "geolocation": ScoringResult(score=0, confidence=0.5),
            "ip_intelligence": ScoringResult(score=30, confidence=0.75),
        }
        result = aggregator.aggregate(scores)
        # Manual: 40*0.25 + 60*0.20 + 80*0.20 + 20*0.15 + 0*0.10 + 30*0.10
        # = 10 + 12 + 16 + 3 + 0 + 3 = 44
        assert abs(result.total_score - 44.0) < 0.1

    def test_missing_module(self, aggregator):
        """Missing module should be treated as 0."""
        scores = {
            "behavior_analyzer": ScoringResult(score=100, confidence=1.0),
        }
        result = aggregator.aggregate(scores)
        assert result.total_score == 25.0  # Only behavior weight

    def test_signals_collected(self, aggregator):
        """All module signals should be collected."""
        scores = {
            "behavior_analyzer": ScoringResult(score=50, confidence=0.8, signals=["Signal A"]),
            "velocity_detector": ScoringResult(score=30, confidence=0.9, signals=["Signal B"]),
            "device_risk": ScoringResult(score=0, confidence=0.5),
            "merchant_risk": ScoringResult(score=0, confidence=0.5),
            "geolocation": ScoringResult(score=0, confidence=0.5),
            "ip_intelligence": ScoringResult(score=0, confidence=0.5, signals=["Signal C"]),
        }
        result = aggregator.aggregate(scores)
        assert "Signal A" in result.signals
        assert "Signal B" in result.signals
        assert "Signal C" in result.signals

    def test_sub_scores_recorded(self, aggregator):
        """Sub scores should be recorded per module."""
        scores = {
            "behavior_analyzer": ScoringResult(score=42.5, confidence=0.8),
            "velocity_detector": ScoringResult(score=0, confidence=0.9),
            "device_risk": ScoringResult(score=0, confidence=0.5),
            "merchant_risk": ScoringResult(score=0, confidence=0.5),
            "geolocation": ScoringResult(score=0, confidence=0.5),
            "ip_intelligence": ScoringResult(score=0, confidence=0.5),
        }
        result = aggregator.aggregate(scores)
        assert result.sub_scores["behavior_analyzer"] == 42.5

    def test_score_capped_at_100(self, aggregator):
        """Even if math exceeds 100, cap at 100."""
        # This shouldn't happen with proper weights but test the cap
        scores = {name: ScoringResult(score=100, confidence=1.0) for name in WEIGHTS}
        result = aggregator.aggregate(scores)
        assert result.total_score <= 100.0
