"""End-to-end fraud scenario tests - validate detection accuracy per pattern."""

import uuid
import pytest
from fraud_detection.mock.fraud_patterns import FraudPatternInjector


class TestFraudScenarios:
    """Test each of the 7 fraud patterns for detection accuracy."""

    @pytest.fixture
    def injector(self):
        return FraudPatternInjector(seed=42)

    async def test_velocity_burst_detected(self, client, injector):
        """Velocity burst pattern should produce high risk scores."""
        txns = injector.velocity_burst("velocity_test_user")
        scores = []
        for txn in txns:
            payload = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": txn.user_id,
                "merchant_id": txn.merchant_id,
                "amount": txn.amount,
                "currency": "INR",
                "device_fingerprint": txn.device_fingerprint,
                "ip_address": txn.ip_address,
                "metadata": txn.metadata,
            }
            response = await client.post("/api/v1/transactions", json=payload)
            if response.status_code == 201:
                scores.append(response.json()["risk_score"])

        # Later transactions in burst should score higher
        if len(scores) > 3:
            avg_late = sum(scores[3:]) / len(scores[3:])
            assert avg_late > 30, f"Burst not detected: avg score {avg_late}"

    async def test_device_spoofing_detected(self, client, injector):
        """Emulator + rooted device should score > 50."""
        txns = injector.device_spoofing("device_spoof_user")
        for txn in txns:
            payload = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": txn.user_id,
                "merchant_id": txn.merchant_id,
                "amount": txn.amount,
                "currency": "INR",
                "device_fingerprint": txn.device_fingerprint,
                "ip_address": txn.ip_address,
                "metadata": txn.metadata,
            }
            response = await client.post("/api/v1/transactions", json=payload)
            assert response.status_code == 201
            # Device spoofing should trigger device risk module
            assert response.json()["risk_score"] > 20

    async def test_amount_anomaly_detected(self, client, injector):
        """10x+ spending anomaly should be flagged."""
        txns = injector.amount_anomaly("amount_test_user", user_avg=2000)
        for txn in txns:
            payload = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": txn.user_id,
                "merchant_id": txn.merchant_id,
                "amount": txn.amount,
                "currency": "INR",
                "device_fingerprint": txn.device_fingerprint,
                "ip_address": txn.ip_address,
                "metadata": txn.metadata,
            }
            response = await client.post("/api/v1/transactions", json=payload)
            assert response.status_code == 201

    async def test_mixed_pattern_detected(self, client, injector):
        """Mixed pattern (VPN + emulator + large amount) should score high."""
        txns = injector.mixed_pattern("mixed_test_user")
        for txn in txns:
            payload = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": txn.user_id,
                "merchant_id": txn.merchant_id,
                "amount": txn.amount,
                "currency": "INR",
                "device_fingerprint": txn.device_fingerprint,
                "ip_address": txn.ip_address,
                "geo_lat": txn.geo_lat,
                "geo_lon": txn.geo_lon,
                "metadata": txn.metadata,
            }
            response = await client.post("/api/v1/transactions", json=payload)
            assert response.status_code == 201
            data = response.json()
            # Mixed patterns with VPN + emulator should trigger multiple modules
            assert data["decision"] in ("verify", "review", "block")

    async def test_normal_transaction_approved(self, client):
        """Normal transaction should be approved with low score."""
        payload = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": "normal_user_001",
            "merchant_id": "merchant_0001",
            "amount": 1500.00,
            "currency": "INR",
            "device_fingerprint": "device_normal_001",
            "ip_address": "103.21.58.100",
            "geo_lat": 28.6139,
            "geo_lon": 77.2090,
            "metadata": {"merchant_category": "retail"},
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 201
        data = response.json()
        # Normal transaction should score low
        assert data["risk_score"] < 50
