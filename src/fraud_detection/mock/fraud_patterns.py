"""7 fraud injection patterns for realistic test data generation."""

import random
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class FraudTransaction:
    """A transaction with fraud indicators injected."""

    user_id: str
    merchant_id: str
    amount: float
    metadata: dict[str, Any]
    device_fingerprint: str | None = None
    ip_address: str | None = None
    geo_lat: float | None = None
    geo_lon: float | None = None
    pattern: str = ""


class FraudPatternInjector:
    """Generates transactions matching specific fraud patterns."""

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def velocity_burst(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 1: 10+ transactions in 1-2 minutes."""
        txns = []
        merchant = f"merchant_{self._rng.randint(1, 500):04d}"
        for i in range(self._rng.randint(10, 15)):
            txns.append(FraudTransaction(
                user_id=user_id,
                merchant_id=merchant,
                amount=round(self._rng.uniform(100, 2000), 2),
                device_fingerprint=f"device_burst_{user_id}",
                ip_address=f"103.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                metadata={"fraud_pattern": "velocity_burst", "burst_index": i},
                pattern="velocity_burst",
            ))
        return txns

    def account_takeover(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 2: New device + password change + large transaction."""
        new_device = f"device_ato_{self._rng.randint(10000, 99999)}"
        return [
            FraudTransaction(
                user_id=user_id,
                merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
                amount=round(self._rng.uniform(50000, 200000), 2),
                device_fingerprint=new_device,
                ip_address=f"185.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                geo_lat=round(self._rng.uniform(40, 55), 4),  # Europe
                geo_lon=round(self._rng.uniform(-5, 25), 4),
                metadata={
                    "fraud_pattern": "account_takeover",
                    "password_changed": True,
                    "ip_is_vpn": True,
                    "device_is_emulator": self._rng.choice([True, False]),
                },
                pattern="account_takeover",
            )
        ]

    def geo_impossible_travel(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 3: Two locations >500km apart in <30 minutes."""
        # First txn in India
        txn1 = FraudTransaction(
            user_id=user_id,
            merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
            amount=round(self._rng.uniform(1000, 10000), 2),
            geo_lat=28.6139,  # Delhi
            geo_lon=77.2090,
            ip_address="103.21.58.1",
            metadata={
                "fraud_pattern": "geo_impossible_travel",
                "last_geo_lat": 28.6139,
                "last_geo_lon": 77.2090,
                "last_txn_time": time.time() - 1800,  # 30 min ago
            },
            pattern="geo_impossible_travel",
        )
        # Second txn in London (7000+ km away, 30 min later)
        txn2 = FraudTransaction(
            user_id=user_id,
            merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
            amount=round(self._rng.uniform(5000, 50000), 2),
            geo_lat=51.5074,  # London
            geo_lon=-0.1278,
            ip_address="185.86.151.11",
            metadata={
                "fraud_pattern": "geo_impossible_travel",
                "last_geo_lat": 28.6139,
                "last_geo_lon": 77.2090,
                "last_txn_time": time.time() - 1800,
            },
            pattern="geo_impossible_travel",
        )
        return [txn1, txn2]

    def card_testing(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 4: Many small amounts (<$1) across different merchants."""
        txns = []
        device = f"device_cardtest_{self._rng.randint(1000, 9999)}"
        for i in range(self._rng.randint(8, 15)):
            txns.append(FraudTransaction(
                user_id=user_id,
                merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
                amount=round(self._rng.uniform(1, 50), 2),
                device_fingerprint=device,
                ip_address=f"45.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                metadata={"fraud_pattern": "card_testing", "ip_is_datacenter": True},
                pattern="card_testing",
            ))
        return txns

    def device_spoofing(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 5: Emulator + rooted device indicators."""
        return [
            FraudTransaction(
                user_id=user_id,
                merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
                amount=round(self._rng.uniform(5000, 100000), 2),
                device_fingerprint=f"emulator_{self._rng.randint(1, 100)}",
                ip_address=f"34.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                metadata={
                    "fraud_pattern": "device_spoofing",
                    "device_is_emulator": True,
                    "device_is_rooted": True,
                    "ip_is_datacenter": True,
                },
                pattern="device_spoofing",
            )
        ]

    def amount_anomaly(self, user_id: str, user_avg: float) -> list[FraudTransaction]:
        """Pattern 6: Amount 10x+ user's average spending."""
        multiplier = self._rng.uniform(10, 50)
        return [
            FraudTransaction(
                user_id=user_id,
                merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
                amount=round(user_avg * multiplier, 2),
                device_fingerprint=f"device_{user_id}",
                ip_address=f"103.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                metadata={"fraud_pattern": "amount_anomaly", "multiplier": multiplier},
                pattern="amount_anomaly",
            )
        ]

    def mixed_pattern(self, user_id: str) -> list[FraudTransaction]:
        """Pattern 7: Combination of 2-3 fraud indicators."""
        return [
            FraudTransaction(
                user_id=user_id,
                merchant_id=f"merchant_{self._rng.randint(1, 500):04d}",
                amount=round(self._rng.uniform(20000, 100000), 2),
                device_fingerprint=f"device_mixed_{self._rng.randint(1000, 9999)}",
                ip_address=f"185.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
                geo_lat=round(self._rng.uniform(-30, 60), 4),
                geo_lon=round(self._rng.uniform(-120, 140), 4),
                metadata={
                    "fraud_pattern": "mixed_pattern",
                    "ip_is_vpn": True,
                    "ip_is_tor": self._rng.choice([True, False]),
                    "device_is_emulator": self._rng.choice([True, False]),
                    "cross_border": True,
                },
                pattern="mixed_pattern",
            )
        ]
