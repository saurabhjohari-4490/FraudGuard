"""Test data factories for generating consistent test objects."""

import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from fraud_detection.schemas.transaction import TransactionCreate


class TransactionFactory:
    """Factory for creating transaction test payloads."""

    _counter = 0

    @classmethod
    def create(cls, **overrides) -> dict:
        """Create a transaction payload dict with sensible defaults."""
        cls._counter += 1
        defaults = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": f"user_{cls._counter:04d}",
            "merchant_id": f"merchant_{random.randint(1, 500):04d}",
            "amount": round(random.uniform(500, 10000), 2),
            "currency": "INR",
            "card_bin": f"{random.randint(400000, 499999)}",
            "device_fingerprint": f"device_{cls._counter}",
            "ip_address": f"103.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "geo_lat": round(random.uniform(8, 35), 4),
            "geo_lon": round(random.uniform(68, 97), 4),
            "channel": "mobile",
            "metadata": {"merchant_category": "retail"},
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def create_pydantic(cls, **overrides) -> TransactionCreate:
        """Create a TransactionCreate Pydantic model."""
        return TransactionCreate(**cls.create(**overrides))

    @classmethod
    def batch(cls, count: int, **shared_overrides) -> list[dict]:
        """Create multiple transaction payloads."""
        return [cls.create(**shared_overrides) for _ in range(count)]


class FraudTransactionFactory:
    """Factory for creating transactions likely to be flagged as fraud."""

    @classmethod
    def high_amount(cls, user_id: str = "fraud_user_001", **overrides) -> dict:
        """Transaction with abnormally high amount."""
        return TransactionFactory.create(
            user_id=user_id,
            amount=round(random.uniform(200000, 500000), 2),
            **overrides,
        )

    @classmethod
    def vpn_emulator(cls, user_id: str = "fraud_user_002", **overrides) -> dict:
        """Transaction from VPN + emulator."""
        return TransactionFactory.create(
            user_id=user_id,
            ip_address=f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            device_fingerprint=f"emulator_{random.randint(1,50)}",
            metadata={"ip_is_vpn": True, "device_is_emulator": True, "merchant_category": "gambling"},
            **overrides,
        )

    @classmethod
    def new_device_high_amount(cls, user_id: str = "fraud_user_003", **overrides) -> dict:
        """High amount from a brand new device."""
        return TransactionFactory.create(
            user_id=user_id,
            amount=round(random.uniform(100000, 300000), 2),
            device_fingerprint=f"new_device_{uuid.uuid4().hex[:8]}",
            **overrides,
        )

    @classmethod
    def velocity_burst(cls, user_id: str = "burst_user_001", count: int = 10, **overrides) -> list[dict]:
        """Multiple rapid transactions from same user."""
        return TransactionFactory.batch(
            count,
            user_id=user_id,
            amount=round(random.uniform(5000, 20000), 2),
            **overrides,
        )


class UserProfileFactory:
    """Factory for user profile data."""

    @classmethod
    def create(cls, **overrides) -> dict:
        """Create user profile attributes."""
        defaults = {
            "user_id": f"user_{random.randint(1, 10000):05d}",
            "avg_transaction_amount": Decimal("3500.00"),
            "transaction_count": random.randint(10, 200),
            "typical_merchants": [f"merchant_{i:04d}" for i in random.sample(range(1, 500), 5)],
            "typical_geo_regions": ["IN"],
            "risk_level": "low",
            "first_seen_at": datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            "last_active_at": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def high_risk(cls, **overrides) -> dict:
        """Create a high-risk user profile."""
        return cls.create(
            risk_level="high",
            avg_transaction_amount=Decimal("50000.00"),
            transaction_count=5,
            first_seen_at=datetime.utcnow() - timedelta(days=2),
            **overrides,
        )


class DeviceProfileFactory:
    """Factory for device profile data."""

    @classmethod
    def create(cls, **overrides) -> dict:
        """Create device profile attributes."""
        defaults = {
            "fingerprint": f"fp_{uuid.uuid4().hex[:16]}",
            "user_ids": [f"user_{random.randint(1, 1000):04d}"],
            "os": random.choice(["Android 14", "iOS 17", "Windows 11"]),
            "browser": random.choice(["Chrome 120", "Safari 17", "Firefox 121"]),
            "screen_resolution": random.choice(["1080x2400", "1170x2532", "1440x3200"]),
            "timezone": "Asia/Kolkata",
            "language": "en",
            "is_emulator": False,
            "is_rooted": False,
            "risk_score": 0.0,
            "first_seen_at": datetime.utcnow() - timedelta(days=random.randint(7, 180)),
            "last_seen_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def suspicious(cls, **overrides) -> dict:
        """Create a suspicious device profile."""
        return cls.create(
            is_emulator=True,
            is_rooted=True,
            user_ids=[f"user_{i:04d}" for i in random.sample(range(1, 100), 5)],
            risk_score=75.0,
            first_seen_at=datetime.utcnow() - timedelta(hours=2),
            **overrides,
        )
