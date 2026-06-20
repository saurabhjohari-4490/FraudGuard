"""Auto-migration runner on application startup."""

import logging

from fraud_detection.db.engine import get_engine
from fraud_detection.models import Base  # noqa: F401 - importing Base populates metadata via __init__

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    """Create all tables if they don't exist.

    Uses SQLAlchemy create_all for development. In production, use Alembic CLI.
    """
    logger.info("Running database migrations...")
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database migrations complete.")
