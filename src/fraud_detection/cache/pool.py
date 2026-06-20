"""Redis connection pool management."""

import logging

from redis.asyncio import ConnectionPool, Redis

from fraud_detection.config import settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None
_redis: Redis | None = None


def get_redis() -> Redis:
    """Get the Redis client instance."""
    global _redis, _pool
    if _redis is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
        _redis = Redis(connection_pool=_pool)
    return _redis


async def init_redis() -> None:
    """Initialize and verify Redis connection."""
    redis = get_redis()
    try:
        await redis.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Operating in degraded mode.")


async def close_redis() -> None:
    """Close Redis connections."""
    global _redis, _pool
    if _redis is not None:
        await _redis.aclose()
        _redis = None
    if _pool is not None:
        await _pool.aclose()
        _pool = None
