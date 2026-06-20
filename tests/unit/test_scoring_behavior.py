"""Unit tests for Behavior Analyzer scoring module."""

import pytest
from decimal import Decimal
from datetime import datetime

from fraud_detection.scoring.behavior import BehaviorAnalyzer
from fraud_detection.services.enrichment import EnrichedContext


@pytest.fixture
def analyzer():
    return BehaviorAnalyzer()


class TestBehaviorAnalyzer:
    async def test_normal_transaction_low_score(self, analyzer, make_scoring_context):
        """Normal transaction matching user profile should score low."""
        context = make_scoring_context(amount=Decimal("2000.00"))
        result = await analyzer.score(context)
        assert result.score < 30
        assert result.confidence > 0.5

    async def test_high_amount_anomaly(self, analyzer, make_scoring_context):
        """Amount 10x user average should score high."""
        context = make_scoring_context(amount=Decimal("25000.00"))  # 12.5x average
        result = await analyzer.score(context)
        assert result.score >= 30
        assert any("higher than user average" in s for s in result.signals)

    async def test_extreme_amount_anomaly(self, analyzer, make_scoring_context):
        """Amount 50x user average should score very high."""
        context = make_scoring_context(amount=Decimal("100000.00"))  # 50x average
        result = await analyzer.score(context)
        assert result.score >= 45

    async def test_first_time_user(self, analyzer, make_scoring_context, sample_enriched_context):
        """First-time user with no history gets a small bump."""
        sample_enriched_context.user_txn_count = 0
        sample_enriched_context.user_avg_amount = 0
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await analyzer.score(context)
        assert result.score >= 10
        assert result.confidence < 0.5

    async def test_new_merchant(self, analyzer, make_scoring_context):
        """Transaction with new merchant triggers signal."""
        context = make_scoring_context(merchant_id="merchant_never_seen_before")
        result = await analyzer.score(context)
        assert any("First transaction with this merchant" in s for s in result.signals)

    async def test_unusual_hours(self, analyzer, make_scoring_context):
        """Transaction at 3 AM triggers time anomaly."""
        context = make_scoring_context(
            timestamp=datetime(2026, 6, 19, 3, 0, 0)  # 3 AM
        )
        result = await analyzer.score(context)
        assert any("unusual hours" in s for s in result.signals)

    @pytest.mark.parametrize("amount,min_expected", [
        (Decimal("2000"), 0),     # 1x avg: no anomaly
        (Decimal("10000"), 15),   # 5x: medium
        (Decimal("25000"), 30),   # 12.5x: high
    ])
    async def test_amount_scaling(self, analyzer, make_scoring_context, amount, min_expected):
        """Scores scale with amount deviation."""
        context = make_scoring_context(amount=amount)
        result = await analyzer.score(context)
        assert result.score >= min_expected

    async def test_score_capped_at_100(self, analyzer, make_scoring_context, sample_enriched_context):
        """Score should never exceed 100."""
        # Trigger all rules simultaneously
        sample_enriched_context.user_typical_merchants = []
        context = make_scoring_context(
            amount=Decimal("500000.00"),  # Extreme amount
            merchant_id="new_merchant",
            timestamp=datetime(2026, 6, 19, 3, 0, 0),  # 3 AM
            enrichment=sample_enriched_context,
        )
        result = await analyzer.score(context)
        assert result.score <= 100
