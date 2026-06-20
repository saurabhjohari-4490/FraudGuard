"""Health check endpoints."""

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from fraud_detection.cache.pool import get_redis
from fraud_detection.db.engine import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Basic liveness check."""
    return {"status": "healthy", "service": "fraud-detection"}


@router.get("/ready")
async def readiness() -> dict:
    """Readiness check - verifies DB and Redis connectivity."""
    checks = {}

    # Check PostgreSQL
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(sa_text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # Check Redis
    try:
        redis: Redis = get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


from sqlalchemy import text as sa_text
