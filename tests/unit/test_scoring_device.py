"""Unit tests for Device Risk Engine scoring module."""

import time
import pytest
from fraud_detection.scoring.device import DeviceRiskEngine
from fraud_detection.services.enrichment import EnrichedContext


@pytest.fixture
def engine():
    return DeviceRiskEngine()


class TestDeviceRiskEngine:
    async def test_normal_device(self, engine, make_scoring_context, sample_enriched_context):
        """Normal device with history should score low."""
        sample_enriched_context.device_is_emulator = False
        sample_enriched_context.device_is_rooted = False
        sample_enriched_context.device_user_count = 1
        sample_enriched_context.device_first_seen = time.time() - 86400
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert result.score < 15

    async def test_emulator(self, engine, make_scoring_context, sample_enriched_context):
        """Emulator should add 40 to score."""
        sample_enriched_context.device_is_emulator = True
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert result.score >= 40
        assert any("emulator" in s.lower() for s in result.signals)

    async def test_rooted_device(self, engine, make_scoring_context, sample_enriched_context):
        """Rooted device should add 30 to score."""
        sample_enriched_context.device_is_rooted = True
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert result.score >= 30

    async def test_new_device(self, engine, make_scoring_context, sample_enriched_context):
        """Device first seen < 5 minutes ago should flag."""
        sample_enriched_context.device_first_seen = time.time() - 120  # 2 min ago
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert any("New device" in s for s in result.signals)

    async def test_shared_device(self, engine, make_scoring_context, sample_enriched_context):
        """Device used by 3+ users should flag."""
        sample_enriched_context.device_user_count = 5
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert any("Shared device" in s for s in result.signals)

    async def test_no_fingerprint(self, engine, make_scoring_context):
        """No device fingerprint should add moderate risk."""
        context = make_scoring_context(device_fingerprint=None)
        result = await engine.score(context)
        assert result.score >= 15
        assert result.confidence < 0.5

    async def test_emulator_and_rooted_combo(self, engine, make_scoring_context, sample_enriched_context):
        """Emulator + rooted should score even higher."""
        sample_enriched_context.device_is_emulator = True
        sample_enriched_context.device_is_rooted = True
        context = make_scoring_context(enrichment=sample_enriched_context)
        result = await engine.score(context)
        assert result.score >= 70
