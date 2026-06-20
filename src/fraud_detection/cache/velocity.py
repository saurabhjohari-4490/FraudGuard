"""Velocity counter using Redis sorted sets."""

import time

from redis.asyncio import Redis


class VelocityCounter:
    """Track transaction velocity per user using Redis sorted sets.

    Key pattern: vel:{user_id}
    Score: timestamp
    Member: {timestamp}:{amount}
    """

    TTL_SECONDS = 86400  # 24 hours

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def record(self, user_id: str, amount: float) -> None:
        """Record a transaction for velocity tracking."""
        now = time.time()
        key = f"vel:{user_id}"
        member = f"{now}:{amount}"

        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.zadd(key, {member: now})
            pipe.zremrangebyscore(key, "-inf", now - self.TTL_SECONDS)
            pipe.expire(key, self.TTL_SECONDS)
            await pipe.execute()

    async def count(self, user_id: str, window_seconds: int) -> int:
        """Count transactions in the given time window."""
        now = time.time()
        key = f"vel:{user_id}"
        return await self._redis.zcount(key, now - window_seconds, now)

    async def sum_amounts(self, user_id: str, window_seconds: int) -> float:
        """Sum transaction amounts in the given time window."""
        now = time.time()
        key = f"vel:{user_id}"
        members = await self._redis.zrangebyscore(key, now - window_seconds, now)
        total = 0.0
        for member in members:
            parts = member.split(":") if isinstance(member, str) else member.decode().split(":")
            if len(parts) >= 2:
                try:
                    total += float(parts[1])
                except ValueError:
                    continue
        return total

    async def get_velocity_profile(self, user_id: str) -> dict:
        """Get velocity counts for all standard windows."""
        counts = {}
        for window_name, seconds in [
            ("1m", 60),
            ("5m", 300),
            ("1h", 3600),
            ("24h", 86400),
        ]:
            counts[window_name] = await self.count(user_id, seconds)
        return counts
