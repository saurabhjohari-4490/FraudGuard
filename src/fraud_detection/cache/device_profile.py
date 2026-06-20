"""Device profile cache using Redis hashes."""

import time

from redis.asyncio import Redis


class DeviceProfileCache:
    """Cache device profile data in Redis hashes.

    Key pattern: device:{fingerprint}
    Fields: user_count, is_emulator, is_rooted, first_seen, last_seen, user_ids
    """

    TTL_SECONDS = 7200  # 2 hours

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, fingerprint: str) -> dict | None:
        """Fetch cached device profile."""
        if not fingerprint:
            return None
        key = f"device:{fingerprint}"
        data = await self._redis.hgetall(key)
        if not data:
            return None
        return {
            "user_count": int(data.get("user_count", 1)),
            "is_emulator": data.get("is_emulator", "0") == "1",
            "is_rooted": data.get("is_rooted", "0") == "1",
            "first_seen": float(data.get("first_seen", 0)),
            "last_seen": float(data.get("last_seen", 0)),
            "user_ids": data.get("user_ids", "").split(",") if data.get("user_ids") else [],
            "risk_score": float(data.get("risk_score", 0)),
        }

    async def set(self, fingerprint: str, profile: dict) -> None:
        """Update cached device profile."""
        key = f"device:{fingerprint}"
        cache_data = {
            "user_count": str(profile.get("user_count", 1)),
            "is_emulator": "1" if profile.get("is_emulator") else "0",
            "is_rooted": "1" if profile.get("is_rooted") else "0",
            "first_seen": str(profile.get("first_seen", time.time())),
            "last_seen": str(profile.get("last_seen", time.time())),
            "user_ids": ",".join(profile.get("user_ids", [])),
            "risk_score": str(profile.get("risk_score", 0)),
        }
        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.hset(key, mapping=cache_data)
            pipe.expire(key, self.TTL_SECONDS)
            await pipe.execute()

    async def record_usage(self, fingerprint: str, user_id: str) -> None:
        """Record device usage by a user."""
        if not fingerprint:
            return
        profile = await self.get(fingerprint) or {
            "user_count": 0,
            "is_emulator": False,
            "is_rooted": False,
            "first_seen": time.time(),
            "last_seen": time.time(),
            "user_ids": [],
            "risk_score": 0,
        }

        user_ids = profile["user_ids"]
        if user_id not in user_ids:
            user_ids.append(user_id)

        profile["user_count"] = len(user_ids)
        profile["user_ids"] = user_ids[-20:]  # Keep last 20
        profile["last_seen"] = time.time()

        await self.set(fingerprint, profile)
