"""Mock user profile generator."""

import random
from dataclasses import dataclass, field


@dataclass
class MockUser:
    user_id: str
    avg_spend: float
    txn_frequency: float  # transactions per day
    typical_merchants: list[str] = field(default_factory=list)
    typical_regions: list[str] = field(default_factory=list)
    risk_level: str = "low"


# Spending profiles
PROFILES = [
    {"name": "low_spender", "avg": 500, "std": 200, "freq": 2, "pct": 0.4},
    {"name": "medium_spender", "avg": 2500, "std": 1000, "freq": 5, "pct": 0.35},
    {"name": "high_spender", "avg": 15000, "std": 5000, "freq": 8, "pct": 0.15},
    {"name": "premium", "avg": 50000, "std": 20000, "freq": 3, "pct": 0.1},
]

REGIONS = ["IN", "US", "EU", "APAC"]


def generate_users(count: int = 1000, seed: int = 42) -> list[MockUser]:
    """Generate mock user profiles with varied spending patterns."""
    rng = random.Random(seed)
    users: list[MockUser] = []

    for i in range(count):
        # Select profile based on distribution
        roll = rng.random()
        cumulative = 0.0
        profile = PROFILES[0]
        for p in PROFILES:
            cumulative += p["pct"]
            if roll <= cumulative:
                profile = p
                break

        avg_spend = max(100, rng.gauss(profile["avg"], profile["std"]))
        freq = max(0.5, rng.gauss(profile["freq"], profile["freq"] * 0.3))

        # Assign typical merchants (3-8 merchants)
        num_merchants = rng.randint(3, 8)
        merchants = [f"merchant_{rng.randint(1, 500)}" for _ in range(num_merchants)]

        # Assign regions (1-2 typical)
        num_regions = rng.choice([1, 1, 1, 2])
        regions = rng.sample(REGIONS, num_regions)

        users.append(MockUser(
            user_id=f"user_{i+1:04d}",
            avg_spend=round(avg_spend, 2),
            txn_frequency=round(freq, 1),
            typical_merchants=merchants,
            typical_regions=regions,
            risk_level="low" if avg_spend < 5000 else "medium",
        ))

    return users
