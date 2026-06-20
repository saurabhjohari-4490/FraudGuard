"""Locust load test for Fraud Detection API."""

import random
import uuid

from locust import HttpUser, between, task


class FraudAPIUser(HttpUser):
    """Simulates API traffic with configurable fraud rate."""

    wait_time = between(0.01, 0.1)

    @task(10)
    def submit_normal_transaction(self):
        """Submit a normal transaction."""
        payload = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": f"user_{random.randint(1, 1000):04d}",
            "merchant_id": f"merchant_{random.randint(1, 500):04d}",
            "amount": round(random.uniform(100, 50000), 2),
            "currency": "INR",
            "device_fingerprint": f"device_{random.randint(1, 200)}",
            "ip_address": f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "geo_lat": round(random.uniform(8, 35), 4),
            "geo_lon": round(random.uniform(68, 97), 4),
            "channel": random.choice(["mobile", "web", "pos"]),
            "metadata": {"merchant_category": random.choice(["retail", "food_delivery", "electronics"])},
        }
        self.client.post("/api/v1/transactions", json=payload)

    @task(1)
    def submit_fraud_transaction(self):
        """Submit a suspicious transaction."""
        payload = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": f"user_{random.randint(1, 1000):04d}",
            "merchant_id": f"merchant_{random.randint(1, 500):04d}",
            "amount": round(random.uniform(50000, 500000), 2),
            "currency": "INR",
            "device_fingerprint": f"emulator_{random.randint(1, 50)}",
            "ip_address": f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "metadata": {
                "ip_is_vpn": True,
                "device_is_emulator": True,
                "merchant_category": "gambling",
            },
        }
        self.client.post("/api/v1/transactions", json=payload)

    @task(3)
    def get_metrics(self):
        """Check metrics endpoint."""
        self.client.get("/api/v1/metrics")

    @task(2)
    def get_alerts(self):
        """Check alerts endpoint."""
        self.client.get("/api/v1/alerts")

    @task(1)
    def search_transactions(self):
        """Search transactions."""
        user_id = f"user_{random.randint(1, 1000):04d}"
        self.client.get(f"/api/v1/transactions?user_id={user_id}")
