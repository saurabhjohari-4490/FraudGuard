"""Security tests for input validation and error handling."""

import pytest


class TestInputValidation:
    async def test_oversized_payload(self, client):
        """Oversized payload should be rejected."""
        payload = {
            "transaction_id": "test",
            "user_id": "u" * 100,  # exceeds max_length=64
            "merchant_id": "merchant_001",
            "amount": 1000,
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 422

    async def test_invalid_amount_zero(self, client):
        """Amount of 0 should be rejected."""
        payload = {
            "transaction_id": "test",
            "user_id": "user_001",
            "merchant_id": "merchant_001",
            "amount": 0,
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 422

    async def test_invalid_currency(self, client):
        """Invalid currency code should be rejected."""
        payload = {
            "transaction_id": "test",
            "user_id": "user_001",
            "merchant_id": "merchant_001",
            "amount": 1000,
            "currency": "INVALID",
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 422

    async def test_invalid_card_bin(self, client):
        """Non-6-digit card bin should be rejected."""
        payload = {
            "transaction_id": "test",
            "user_id": "user_001",
            "merchant_id": "merchant_001",
            "amount": 1000,
            "card_bin": "12345",  # Only 5 digits
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 422

    async def test_invalid_geo_lat(self, client):
        """Latitude > 90 should be rejected."""
        payload = {
            "transaction_id": "test",
            "user_id": "user_001",
            "merchant_id": "merchant_001",
            "amount": 1000,
            "geo_lat": 100,  # Invalid
        }
        response = await client.post("/api/v1/transactions", json=payload)
        assert response.status_code == 422

    async def test_error_response_no_stack_trace(self, client):
        """Error responses should not expose internal details."""
        response = await client.get("/api/v1/fraud/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "traceback" not in str(data).lower()
        assert "sqlalchemy" not in str(data).lower()
        assert "file" not in str(data).lower()
