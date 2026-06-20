"""Unit tests for IP intelligence scoring module."""

import pytest

from fraud_detection.scoring.ip_intelligence import IPIntelligence


class TestIPIntelligence:
    @pytest.fixture
    def engine(self):
        return IPIntelligence()

    @pytest.mark.asyncio
    async def test_normal_ip(self, engine, make_scoring_context):
        """Normal Indian IP should score low."""
        ctx = make_scoring_context(
            ip_address="103.21.58.100",
            metadata={},
        )
        result = await engine.score(ctx)
        assert result.score < 15

    @pytest.mark.asyncio
    async def test_no_ip(self, engine, make_scoring_context):
        """No IP address should return low-confidence signal."""
        ctx = make_scoring_context(ip_address=None, metadata={})
        result = await engine.score(ctx)
        assert result.score == 5
        assert result.confidence == 0.3
        assert "No IP address" in result.signals[0]

    @pytest.mark.asyncio
    async def test_vpn_detected(self, engine, make_scoring_context):
        """VPN flag should add 25 to score."""
        ctx = make_scoring_context(
            ip_address="185.100.85.200",
            metadata={"ip_is_vpn": True},
        )
        result = await engine.score(ctx)
        assert result.score >= 25
        assert any("VPN" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_tor_detected(self, engine, make_scoring_context):
        """TOR exit node should score very high."""
        ctx = make_scoring_context(
            ip_address="185.220.101.1",
            metadata={"ip_is_tor": True},
        )
        result = await engine.score(ctx)
        assert result.score >= 45
        assert any("TOR" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_proxy_detected(self, engine, make_scoring_context):
        """Proxy should add 20 to score."""
        ctx = make_scoring_context(
            ip_address="91.192.100.5",
            metadata={"ip_is_proxy": True},
        )
        result = await engine.score(ctx)
        assert result.score >= 20
        assert any("Proxy" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_datacenter_ip_metadata(self, engine, make_scoring_context):
        """Datacenter IP flag from metadata."""
        ctx = make_scoring_context(
            ip_address="45.33.10.1",
            metadata={"ip_is_datacenter": True},
        )
        result = await engine.score(ctx)
        assert result.score >= 20
        assert any("Datacenter" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_datacenter_ip_heuristic(self, engine, make_scoring_context):
        """Known datacenter IP prefix detection."""
        ctx = make_scoring_context(
            ip_address="52.1.2.3",  # AWS range
            metadata={},
        )
        result = await engine.score(ctx)
        assert result.score >= 20
        assert any("Datacenter" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_private_ip(self, engine, make_scoring_context):
        """Private IP should trigger signal."""
        ctx = make_scoring_context(
            ip_address="192.168.1.1",
            metadata={},
        )
        result = await engine.score(ctx)
        assert result.score >= 15
        assert any("Private IP" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_loopback_ip(self, engine, make_scoring_context):
        """Loopback address is highly suspicious."""
        ctx = make_scoring_context(
            ip_address="127.0.0.1",
            metadata={},
        )
        result = await engine.score(ctx)
        assert result.score >= 30
        assert any("Loopback" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_multiple_risk_indicators(self, engine, make_scoring_context):
        """Multiple IP risk flags should compound."""
        ctx = make_scoring_context(
            ip_address="185.220.101.1",
            metadata={"ip_is_vpn": True, "ip_is_tor": True},
        )
        result = await engine.score(ctx)
        # VPN(25) + TOR(45) + multiple indicators(15)
        assert result.score >= 70
        assert any("Multiple IP risk" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_ip_country_mismatch(self, engine, make_scoring_context):
        """IP country mismatch with geo should add risk."""
        ctx = make_scoring_context(
            ip_address="103.21.58.100",
            metadata={"ip_country": "US", "geo_country": "IN"},
        )
        result = await engine.score(ctx)
        assert result.score >= 15
        assert any("doesn't match" in s for s in result.signals)

    @pytest.mark.asyncio
    async def test_score_capped_at_100(self, engine, make_scoring_context):
        """Score never exceeds 100 even with many risk factors."""
        ctx = make_scoring_context(
            ip_address="127.0.0.1",
            metadata={
                "ip_is_vpn": True,
                "ip_is_tor": True,
                "ip_is_proxy": True,
                "ip_is_datacenter": True,
                "ip_country": "US",
                "geo_country": "IN",
            },
        )
        result = await engine.score(ctx)
        assert result.score <= 100
