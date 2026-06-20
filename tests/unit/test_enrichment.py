"""Unit tests for the enrichment service."""

import pytest
from unittest.mock import AsyncMock, patch

from fraud_detection.services.enrichment import EnrichedContext, FeatureEnrichmentService


class TestEnrichedContext:
    def test_defaults(self):
        """Default context has safe zero values."""
        ctx = EnrichedContext()
        assert ctx.velocity_1m == 0
        assert ctx.user_avg_amount == 0.0
        assert ctx.device_is_emulator is False
        assert ctx.partial is False

    def test_custom_values(self):
        """Context accepts custom values."""
        ctx = EnrichedContext(
            velocity_1m=5,
            velocity_5m=12,
            user_avg_amount=5000.0,
            device_is_emulator=True,
        )
        assert ctx.velocity_1m == 5
        assert ctx.velocity_5m == 12
        assert ctx.user_avg_amount == 5000.0
        assert ctx.device_is_emulator is True


class TestFeatureEnrichmentService:
    @pytest.fixture
    def mock_velocity(self):
        mock = AsyncMock()
        mock.get_velocity_profile = AsyncMock(return_value={
            "1m": 2, "5m": 5, "1h": 15, "24h": 40
        })
        mock.record = AsyncMock()
        return mock

    @pytest.fixture
    def mock_user_cache(self):
        mock = AsyncMock()
        mock.get = AsyncMock(return_value={
            "avg_amount": 3000.0,
            "txn_count": 100,
            "typical_merchants": ["merchant_001"],
            "typical_geo_regions": ["IN"],
            "risk_level": "low",
        })
        mock.update_on_transaction = AsyncMock()
        return mock

    @pytest.fixture
    def mock_device_cache(self):
        mock = AsyncMock()
        mock.get = AsyncMock(return_value={
            "user_count": 1,
            "is_emulator": False,
            "is_rooted": False,
            "first_seen": 1700000000.0,
            "risk_score": 5.0,
        })
        mock.record_usage = AsyncMock()
        return mock

    @pytest.fixture
    def service(self, mock_velocity, mock_user_cache, mock_device_cache):
        return FeatureEnrichmentService(
            velocity=mock_velocity,
            user_cache=mock_user_cache,
            device_cache=mock_device_cache,
        )

    @pytest.mark.asyncio
    @patch("fraud_detection.services.enrichment.settings")
    async def test_full_enrichment(self, mock_settings, service):
        """Successful enrichment populates all fields."""
        mock_settings.enrichment_timeout_ms = 50

        result = await service.enrich("user_001", "device_001", 2500.0)

        assert result.velocity_1m == 2
        assert result.velocity_5m == 5
        assert result.velocity_1h == 15
        assert result.velocity_24h == 40
        assert result.user_avg_amount == 3000.0
        assert result.user_txn_count == 100
        assert result.device_user_count == 1
        assert result.device_is_emulator is False
        assert result.partial is False
        assert result.enrichment_time_ms > 0

    @pytest.mark.asyncio
    @patch("fraud_detection.services.enrichment.settings")
    async def test_no_device_fingerprint(self, mock_settings, service):
        """None device fingerprint returns safe defaults."""
        mock_settings.enrichment_timeout_ms = 50

        result = await service.enrich("user_001", None, 1000.0)
        # Device cache should handle None fingerprint gracefully
        assert result.device_user_count == 0
        assert result.device_is_emulator is False

    @pytest.mark.asyncio
    @patch("fraud_detection.services.enrichment.settings")
    async def test_partial_enrichment_on_failure(self, mock_settings, service, mock_velocity):
        """If velocity fails, result is partial but still populated."""
        mock_settings.enrichment_timeout_ms = 50
        mock_velocity.get_velocity_profile = AsyncMock(side_effect=RuntimeError("Redis down"))

        result = await service.enrich("user_001", "device_001", 2500.0)

        assert result.partial is True
        # Velocity defaults to 0
        assert result.velocity_1m == 0
        # User and device still populated
        assert result.user_avg_amount == 3000.0
        assert result.device_user_count == 1

    @pytest.mark.asyncio
    @patch("fraud_detection.services.enrichment.settings")
    async def test_records_transaction(self, mock_settings, service, mock_velocity, mock_user_cache, mock_device_cache):
        """Enrichment records the transaction for future lookups."""
        mock_settings.enrichment_timeout_ms = 50

        await service.enrich("user_001", "device_001", 2500.0)

        mock_velocity.record.assert_called_once_with("user_001", 2500.0)
        mock_user_cache.update_on_transaction.assert_called_once_with("user_001", 2500.0, "")
        mock_device_cache.record_usage.assert_called_once_with("device_001", "user_001")
