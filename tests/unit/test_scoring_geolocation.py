"""Unit tests for geolocation scoring module."""

import pytest
from datetime import datetime, timedelta

from fraud_detection.scoring.geolocation import GeolocationEngine, haversine_distance_km


class TestHaversineDistance:
    def test_same_point(self):
        """Distance from a point to itself is 0."""
        assert haversine_distance_km(28.6, 77.2, 28.6, 77.2) == pytest.approx(0, abs=0.01)

    def test_delhi_to_mumbai(self):
        """Delhi to Mumbai is roughly 1150km."""
        dist = haversine_distance_km(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100 < dist < 1200

    def test_delhi_to_new_york(self):
        """Delhi to New York is roughly 11750km."""
        dist = haversine_distance_km(28.6139, 77.2090, 40.7128, -74.0060)
        assert 11500 < dist < 12000


class TestGeolocationEngine:
    @pytest.fixture
    def engine(self):
        return GeolocationEngine()

    @pytest.mark.asyncio
    async def test_no_geo_data(self, engine, make_scoring_context):
        """No geolocation should return low confidence."""
        ctx = make_scoring_context(geo_lat=None, geo_lon=None)
        result = await engine.score(ctx)
        assert result.score == 0
        assert result.confidence == 0.2
        assert "No geolocation data" in result.signals

    @pytest.mark.asyncio
    async def test_normal_indian_transaction(self, engine, make_scoring_context):
        """Transaction within India from Indian user should be low risk."""
        ctx = make_scoring_context(
            geo_lat=19.07,
            geo_lon=72.87,
        )
        result = await engine.score(ctx)
        # User's typical region is "IN" and transaction is from India
        assert result.score < 30

    @pytest.mark.asyncio
    async def test_new_geographic_region(self, engine, make_scoring_context, sample_enriched_context):
        """Transaction from new region triggers signal."""
        sample_enriched_context.user_typical_geo_regions = ["IN"]
        ctx = make_scoring_context(
            geo_lat=40.7,   # New York area
            geo_lon=-74.0,
            enrichment=sample_enriched_context,
        )
        result = await engine.score(ctx)
        assert result.score >= 25
        assert any("new geographic region" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_impossible_travel(self, engine, make_scoring_context):
        """Impossible travel speed should score very high."""
        now = datetime.utcnow()
        ctx = make_scoring_context(
            geo_lat=40.7,  # New York
            geo_lon=-74.0,
            timestamp=now,
            metadata={
                "last_geo_lat": 28.6,   # Delhi
                "last_geo_lon": 77.2,
                "last_txn_time": (now - timedelta(minutes=30)).timestamp(),
            },
        )
        result = await engine.score(ctx)
        # Delhi to NY in 30 min = ~23500 km/h, impossible
        assert result.score >= 60
        assert any("Impossible travel" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_suspicious_travel_speed(self, engine, make_scoring_context):
        """Fast but not impossible travel triggers suspicious signal."""
        now = datetime.utcnow()
        ctx = make_scoring_context(
            geo_lat=19.07,  # Mumbai
            geo_lon=72.87,
            timestamp=now,
            metadata={
                "last_geo_lat": 28.6,   # Delhi
                "last_geo_lon": 77.2,
                "last_txn_time": (now - timedelta(hours=1.5)).timestamp(),
            },
        )
        result = await engine.score(ctx)
        # Delhi to Mumbai (~1150km) in 1.5h = ~767 km/h
        assert result.score >= 30
        assert any("Suspicious travel" in s or "Impossible travel" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_high_risk_region(self, engine, make_scoring_context):
        """Transaction from high-risk region should add to score."""
        ctx = make_scoring_context(
            geo_lat=28.6,
            geo_lon=77.2,
            metadata={"geo_risk_region": "HIGH_RISK_ZONE"},
        )
        result = await engine.score(ctx)
        assert result.score >= 20
        assert any("high-risk region" in s for s in result.signals)
