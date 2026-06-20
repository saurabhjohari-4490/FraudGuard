"""Unit tests for Decision Engine."""

import pytest
from fraud_detection.services.decision_engine import DecisionEngine, Decision
from fraud_detection.services.risk_aggregator import AggregatedRisk


@pytest.fixture
def engine():
    return DecisionEngine()


class TestDecisionEngine:
    @pytest.mark.parametrize("score,expected_decision", [
        (0, "approve"),
        (15, "approve"),
        (30, "approve"),
        (31, "verify"),
        (45, "verify"),
        (60, "verify"),
        (61, "review"),
        (75, "review"),
        (80, "review"),
        (81, "block"),
        (95, "block"),
        (100, "block"),
    ])
    def test_threshold_boundaries(self, engine, score, expected_decision):
        """Test all decision threshold boundaries."""
        aggregated = AggregatedRisk(
            total_score=score,
            sub_scores={"behavior_analyzer": score},
            confidence=0.8,
            signals=["Test signal"],
        )
        result = engine.decide(aggregated)
        assert result.decision == expected_decision

    def test_explanation_generated(self, engine):
        """Decision should always include an explanation."""
        aggregated = AggregatedRisk(
            total_score=75.0,
            sub_scores={"velocity_detector": 60, "device_risk": 50},
            confidence=0.9,
            signals=["Velocity burst detected", "Emulator detected"],
        )
        result = engine.decide(aggregated)
        assert result.explanation
        assert len(result.explanation) > 20

    def test_signals_preserved(self, engine):
        """Signals from aggregation should be in result."""
        signals = ["Signal 1", "Signal 2", "Signal 3"]
        aggregated = AggregatedRisk(
            total_score=50.0,
            sub_scores={},
            confidence=0.5,
            signals=signals,
        )
        result = engine.decide(aggregated)
        assert result.signals == signals

    def test_sub_scores_preserved(self, engine):
        """Sub scores should pass through to result."""
        sub_scores = {"behavior_analyzer": 30, "velocity_detector": 50}
        aggregated = AggregatedRisk(
            total_score=40.0,
            sub_scores=sub_scores,
            confidence=0.7,
            signals=[],
        )
        result = engine.decide(aggregated)
        assert result.sub_scores == sub_scores
