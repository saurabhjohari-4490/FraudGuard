"""User profile cache using Redis hashes."""

from redis.asyncio import Redis


class UserProfileCache:
    """Cache user profile data in Redis hashes.

    Key pattern: user:{user_id}
    Fields: avg_amount, txn_count, typical_merchants (comma-separated), risk_level
    """

    TTL_SECONDS = 3600  # 1 hour

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, user_id: str) -> dict | None:
        """Fetch cached user profile."""
        key = f"user:{user_id}"
        data = await self._redis.hgetall(key)
        if not data:
            return None
        return {
            "avg_amount": float(data.get("avg_amount", 0)),
            "txn_count": int(data.get("txn_count", 0)),
            "typical_merchants": data.get("typical_merchants", "").split(",") if data.get("typical_merchants") else [],
            "risk_level": data.get("risk_level", "low"),
            "typical_geo_regions": data.get("typical_geo_regions", "").split(",") if data.get("typical_geo_regions") else [],
        }

    async def set(self, user_id: str, profile: dict) -> None:
        """Update cached user profile."""
        key = f"user:{user_id}"
        cache_data = {
            "avg_amount": str(profile.get("avg_amount", 0)),
            "txn_count": str(profile.get("txn_count", 0)),
            "typical_merchants": ",".join(profile.get("typical_merchants", [])),
            "risk_level": profile.get("risk_level", "low"),
            "typical_geo_regions": ",".join(profile.get("typical_geo_regions", [])),
        }
        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.hset(key, mapping=cache_data)
            pipe.expire(key, self.TTL_SECONDS)
            await pipe.execute()

    async def update_on_transaction(self, user_id: str, amount: float, merchant_id: str) -> None:
        """Incrementally update user profile after a transaction."""
        profile = await self.get(user_id) or {
            "avg_amount": 0,
            "txn_count": 0,
            "typical_merchants": [],
            "risk_level": "low",
        }

        count = profile["txn_count"] + 1
        new_avg = ((profile["avg_amount"] * profile["txn_count"]) + amount) / count

        merchants = profile["typical_merchants"]
        if merchant_id not in merchants:
            merchants = (merchants + [merchant_id])[-10:]  # Keep last 10

        profile["avg_amount"] = new_avg
        profile["txn_count"] = count
        profile["typical_merchants"] = merchants

        await self.set(user_id, profile)
