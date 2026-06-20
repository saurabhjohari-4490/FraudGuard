"""Integration tests for Transaction API."""

import uuid
import pytest


class TestTransactionAPI:
    async def test_create_transaction_success(self, client, sample_transaction_payload):
        """POST /api/v1/transactions with valid payload returns 201."""
        response = await client.post("/api/v1/transactions", json=sample_transaction_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_id"] == sample_transaction_payload["transaction_id"]
        assert "risk_score" in data
        assert "decision" in data
        assert data["decision"] in ("approve", "verify", "review", "block")
        assert data["processing_time_ms"] > 0

    async def test_create_transaction_invalid_payload(self, client):
        """POST with missing required fields returns 422."""
        response = await client.post("/api/v1/transactions", json={"amount": 100})
        assert response.status_code == 422

    async def test_create_transaction_invalid_amount(self, client, sample_transaction_payload):
        """POST with negative amount returns 422."""
        sample_transaction_payload["amount"] = -100
        response = await client.post("/api/v1/transactions", json=sample_transaction_payload)
        assert response.status_code == 422

    async def test_create_transaction_duplicate(self, client, sample_transaction_payload):
        """POST with same transaction_id twice returns 409."""
        await client.post("/api/v1/transactions", json=sample_transaction_payload)
        response = await client.post("/api/v1/transactions", json=sample_transaction_payload)
        assert response.status_code == 409

    async def test_list_transactions(self, client, sample_transaction_payload):
        """GET /api/v1/transactions returns list."""
        # Create a transaction first
        sample_transaction_payload["transaction_id"] = str(uuid.uuid4())
        await client.post("/api/v1/transactions", json=sample_transaction_payload)

        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_list_transactions_with_filter(self, client, sample_transaction_payload):
        """GET /api/v1/transactions?user_id=... filters correctly."""
        sample_transaction_payload["transaction_id"] = str(uuid.uuid4())
        sample_transaction_payload["user_id"] = "unique_user_filter_test"
        await client.post("/api/v1/transactions", json=sample_transaction_payload)

        response = await client.get("/api/v1/transactions", params={"user_id": "unique_user_filter_test"})
        assert response.status_code == 200
        data = response.json()
        for txn in data["transactions"]:
            assert txn["user_id"] == "unique_user_filter_test"
