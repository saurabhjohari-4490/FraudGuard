"""Unit tests for merchant risk scoring module."""

import pytest
from decimal import Decimal

from fraud_detection.scoring.merchant import MerchantRiskEngine


class TestMerchantRiskEngine:
    @pytest.fixture
    def engine(self):
        return MerchantRiskEngine()

    @pytest.mark.asyncio
    async def test_normal_merchant(self, engine, make_scoring_context):
        """Normal retail merchant with familiar user should score low."""
        ctx = make_scoring_context(
            merchant_id="merchant_0001",
            metadata={"merchant_category": "retail"},
        )
        result = await engine.score(ctx)
        # Known merchant from user's typical list
        assert result.score < 20

    @pytest.mark.asyncio
    async def test_gambling_category(self, engine, make_scoring_context):
        """Gambling merchants should score high."""
        ctx = make_scoring_context(
            merchant_id="casino_online_001",
            metadata={"merchant_category": "gambling"},
        )
        result = await engine.score(ctx)
        assert result.score >= 30
        assert any("gambling" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_crypto_category(self, engine, make_scoring_context):
        """Crypto merchants should have elevated risk."""
        ctx = make_scoring_context(
            merchant_id="crypto_exchange_001",
            metadata={"merchant_category": "crypto"},
        )
        result = await engine.score(ctx)
        assert result.score >= 25
        assert any("crypto" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_suspicious_name_pattern(self, engine, make_scoring_context):
        """Merchants with test/demo prefix should score higher."""
        ctx = make_scoring_context(
            merchant_id="test_merchant_001",
            metadata={"merchant_category": "retail"},
        )
        result = await engine.score(ctx)
        assert result.score >= 20
        assert any("Suspicious merchant name" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_new_merchant_for_user(self, engine, make_scoring_context, sample_enriched_context):
        """First-time merchant should add risk signal."""
        sample_enriched_context.user_typical_merchants = ["merchant_0001", "merchant_0010"]
        ctx = make_scoring_context(
            merchant_id="merchant_9999",  # Not in typical list
            metadata={"merchant_category": "retail"},
            enrichment=sample_enriched_context,
        )
        result = await engine.score(ctx)
        assert any("New merchant" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_high_amount_at_high_risk(self, engine, make_scoring_context):
        """Large transaction at high-risk merchant should compound."""
        ctx = make_scoring_context(
            merchant_id="some_gambling_site",
            amount=Decimal("75000.00"),
            metadata={"merchant_category": "gambling"},
        )
        result = await engine.score(ctx)
        assert result.score >= 45
        assert any("Large transaction" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_cross_border(self, engine, make_scoring_context):
        """Cross-border transaction adds risk."""
        ctx = make_scoring_context(
            metadata={"merchant_category": "retail", "cross_border": True},
        )
        result = await engine.score(ctx)
        assert any("Cross-border" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_score_capped_at_100(self, engine, make_scoring_context, sample_enriched_context):
        """Score should never exceed 100."""
        sample_enriched_context.user_typical_merchants = []
        ctx = make_scoring_context(
            merchant_id="test_gambling_extreme",
            amount=Decimal("100000.00"),
            metadata={"merchant_category": "gambling", "cross_border": True},
            enrichment=sample_enriched_context,
        )
        result = await engine.score(ctx)
        assert result.score <= 100
