"""Mock merchant generator."""

import random
from dataclasses import dataclass


CATEGORIES = [
    "retail",
    "food_delivery",
    "electronics",
    "travel",
    "digital_goods",
    "gambling",
]

CATEGORY_WEIGHTS = {
    "retail": 0.30,
    "food_delivery": 0.25,
    "electronics": 0.15,
    "travel": 0.12,
    "digital_goods": 0.13,
    "gambling": 0.05,
}


@dataclass
class MockMerchant:
    merchant_id: str
    name: str
    category: str
    avg_transaction: float
    fraud_rate: float  # Historical fraud rate for this merchant


def generate_merchants(count: int = 500, seed: int = 42) -> list[MockMerchant]:
    """Generate mock merchant profiles across 6 categories."""
    rng = random.Random(seed)
    merchants: list[MockMerchant] = []

    category_list = list(CATEGORY_WEIGHTS.keys())
    category_probs = list(CATEGORY_WEIGHTS.values())

    prefixes = {
        "retail": ["MegaMart", "ShopEasy", "ValueStore", "QuickBuy", "DailyDeals"],
        "food_delivery": ["FoodDash", "MealBox", "EatNow", "TastyBites", "OrderIn"],
        "electronics": ["TechZone", "GadgetWorld", "DigitalHub", "ByteShop", "CircuitCity"],
        "travel": ["FlyNow", "StayEasy", "TripGo", "WanderBook", "JetSet"],
        "digital_goods": ["GameVault", "AppStore", "StreamPlus", "CloudPay", "PixelMart"],
        "gambling": ["BetKing", "LuckyStar", "WinBig", "JackpotCity", "SpinMaster"],
    }

    base_fraud_rates = {
        "retail": 0.02,
        "food_delivery": 0.015,
        "electronics": 0.04,
        "travel": 0.03,
        "digital_goods": 0.05,
        "gambling": 0.08,
    }

    base_avg_txn = {
        "retail": 1500,
        "food_delivery": 500,
        "electronics": 8000,
        "travel": 15000,
        "digital_goods": 300,
        "gambling": 2000,
    }

    for i in range(count):
        # Select category
        category = rng.choices(category_list, weights=category_probs, k=1)[0]

        # Generate name
        prefix = rng.choice(prefixes[category])
        name = f"{prefix}_{i+1:03d}"

        # Fraud rate with some variance
        fraud_rate = max(0.001, rng.gauss(base_fraud_rates[category], base_fraud_rates[category] * 0.5))

        # Average transaction amount
        avg_txn = max(100, rng.gauss(base_avg_txn[category], base_avg_txn[category] * 0.3))

        merchants.append(MockMerchant(
            merchant_id=f"merchant_{i+1:04d}",
            name=name,
            category=category,
            avg_transaction=round(avg_txn, 2),
            fraud_rate=round(fraud_rate, 4),
        ))

    return merchants
