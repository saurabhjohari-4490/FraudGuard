"""Mock transaction generator with configurable TPS and fraud injection."""

import random
import uuid
from datetime import datetime

from fraud_detection.mock.fraud_patterns import FraudPatternInjector, FraudTransaction
from fraud_detection.mock.merchants import MockMerchant, generate_merchants
from fraud_detection.mock.users import MockUser, generate_users
from fraud_detection.schemas.transaction import TransactionCreate


class TransactionGenerator:
    """Generates realistic mock transactions with configurable fraud rate."""

    def __init__(self, seed: int = 42, fraud_rate: float = 0.05) -> None:
        self._rng = random.Random(seed)
        self._fraud_rate = fraud_rate
        self._users = generate_users(1000, seed)
        self._merchants = generate_merchants(500, seed)
        self._injector = FraudPatternInjector(seed)
        self._patterns = [
            "velocity_burst",
            "account_takeover",
            "geo_impossible_travel",
            "card_testing",
            "device_spoofing",
            "amount_anomaly",
            "mixed_pattern",
        ]

    def generate_normal(self) -> TransactionCreate:
        """Generate a single normal (non-fraud) transaction."""
        user = self._rng.choice(self._users)
        merchant = self._rng.choice(self._merchants)

        # Amount based on user's spending profile with variance
        amount = max(10, self._rng.gauss(user.avg_spend, user.avg_spend * 0.4))

        return TransactionCreate(
            transaction_id=str(uuid.uuid4()),
            user_id=user.user_id,
            merchant_id=merchant.merchant_id,
            amount=round(amount, 2),
            currency="INR",
            device_fingerprint=f"device_{user.user_id}_{self._rng.randint(1, 3)}",
            ip_address=f"103.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}.{self._rng.randint(1,255)}",
            geo_lat=round(self._rng.uniform(8, 35), 4),  # India
            geo_lon=round(self._rng.uniform(68, 97), 4),
            channel=self._rng.choice(["mobile", "web", "pos", "api"]),
            metadata={"merchant_category": merchant.category, "is_fraud": False},
            timestamp=datetime.utcnow(),
        )

    def generate_fraud(self) -> list[TransactionCreate]:
        """Generate fraud transaction(s) using a random pattern."""
        user = self._rng.choice(self._users)
        pattern = self._rng.choice(self._patterns)

        fraud_txns: list[FraudTransaction] = []

        if pattern == "velocity_burst":
            fraud_txns = self._injector.velocity_burst(user.user_id)
        elif pattern == "account_takeover":
            fraud_txns = self._injector.account_takeover(user.user_id)
        elif pattern == "geo_impossible_travel":
            fraud_txns = self._injector.geo_impossible_travel(user.user_id)
        elif pattern == "card_testing":
            fraud_txns = self._injector.card_testing(user.user_id)
        elif pattern == "device_spoofing":
            fraud_txns = self._injector.device_spoofing(user.user_id)
        elif pattern == "amount_anomaly":
            fraud_txns = self._injector.amount_anomaly(user.user_id, user.avg_spend)
        elif pattern == "mixed_pattern":
            fraud_txns = self._injector.mixed_pattern(user.user_id)

        # Convert to TransactionCreate
        results = []
        for ft in fraud_txns:
            ft.metadata["is_fraud"] = True
            results.append(TransactionCreate(
                transaction_id=str(uuid.uuid4()),
                user_id=ft.user_id,
                merchant_id=ft.merchant_id,
                amount=round(ft.amount, 2),
                currency="INR",
                device_fingerprint=ft.device_fingerprint,
                ip_address=ft.ip_address,
                geo_lat=ft.geo_lat,
                geo_lon=ft.geo_lon,
                channel="api",
                metadata=ft.metadata,
                timestamp=datetime.utcnow(),
            ))

        return results

    def generate_batch(self, count: int) -> list[TransactionCreate]:
        """Generate a batch of transactions with configured fraud rate."""
        transactions: list[TransactionCreate] = []
        fraud_count = int(count * self._fraud_rate)
        normal_count = count - fraud_count

        # Generate normal transactions
        for _ in range(normal_count):
            transactions.append(self.generate_normal())

        # Generate fraud transactions
        fraud_generated = 0
        while fraud_generated < fraud_count:
            fraud_txns = self.generate_fraud()
            for txn in fraud_txns:
                if fraud_generated >= fraud_count:
                    break
                transactions.append(txn)
                fraud_generated += 1

        # Shuffle
        self._rng.shuffle(transactions)
        return transactions
