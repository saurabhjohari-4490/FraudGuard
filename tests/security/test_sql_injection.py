"""Security tests for SQL injection prevention."""

import pytest


SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE transactions; --",
    "1 OR 1=1",
    "' UNION SELECT * FROM fraud_decisions --",
    "1; SELECT * FROM user_profiles",
    "' OR '1'='1",
]


class TestSQLInjection:
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_transaction_search_safe(self, client, payload):
        """SQL injection in search params should not execute."""
        response = await client.get("/api/v1/transactions", params={"q": payload})
        # Should return 200 with no results, not a 500 error
        assert response.status_code == 200

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    async def test_user_id_safe(self, client, payload):
        """SQL injection in user_id should not execute."""
        response = await client.get(f"/api/v1/users/{payload}/risk-profile")
        # Should return 404 (user not found), not 500
        assert response.status_code in (404, 422)

    async def test_json_payload_safe(self, client):
        """SQL injection in JSON body should be safely parameterized."""
        payload = {
            "transaction_id": "test-123",
            "user_id": "'; DROP TABLE transactions; --",
            "merchant_id": "merchant_001",
            "amount": 1000,
        }
        response = await client.post("/api/v1/transactions", json=payload)
        # Should either succeed (string stored safely) or validate (422)
        assert response.status_code in (201, 422)
