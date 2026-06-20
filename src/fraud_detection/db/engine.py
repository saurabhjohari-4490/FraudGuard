"""Async SQLAlchemy engine management."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from fraud_detection.config import settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=not settings.is_production,
        )
    return _engine


async def init_db() -> None:
    """Initialize the database engine."""
    get_engine()


async def close_db() -> None:
    """Dispose the database engine."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
