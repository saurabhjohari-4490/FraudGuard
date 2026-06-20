"""Integration tests for health check endpoints."""

import pytest


class TestHealthEndpoints:
    async def test_health(self, client):
        """GET /health should return 200 with healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "fraud-detection"

    async def test_readiness(self, client):
        """GET /ready should return 200 with service checks."""
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
