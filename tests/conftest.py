"""Shared test fixtures."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fraud_detection.config import settings
from fraud_detection.models import Base
from fraud_detection.main import create_app
from fraud_detection.db.session import get_db
from fraud_detection.scoring.base import TransactionContext
from fraud_detection.services.enrichment import EnrichedContext


# Use a separate test database
TEST_DB_URL = settings.database_url.replace("/fraud_detection", "/fraud_test")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with dependency overrides."""
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def sample_transaction_payload() -> dict:
    """Sample valid transaction payload."""
    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": "user_0001",
        "merchant_id": "merchant_0001",
        "amount": 2500.00,
        "currency": "INR",
        "device_fingerprint": "device_user_0001_1",
        "ip_address": "103.21.58.100",
        "geo_lat": 28.6139,
        "geo_lon": 77.2090,
        "channel": "mobile",
        "metadata": {"merchant_category": "retail"},
    }


@pytest.fixture
def sample_enriched_context() -> EnrichedContext:
    """Sample enriched context for unit tests."""
    return EnrichedContext(
        velocity_1m=1,
        velocity_5m=3,
        velocity_1h=10,
        velocity_24h=25,
        user_avg_amount=2000.0,
        user_txn_count=50,
        user_typical_merchants=["merchant_0001", "merchant_0010", "merchant_0020"],
        user_typical_geo_regions=["IN"],
        user_risk_level="low",
        device_user_count=1,
        device_is_emulator=False,
        device_is_rooted=False,
        device_first_seen=1700000000.0,
        device_risk_score=0.0,
        enrichment_time_ms=10.0,
        partial=False,
    )


@pytest.fixture
def make_scoring_context(sample_enriched_context):
    """Factory for creating TransactionContext with customizable fields."""
    def _make(**kwargs) -> TransactionContext:
        defaults = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": "user_0001",
            "merchant_id": "merchant_0001",
            "amount": Decimal("2500.00"),
            "currency": "INR",
            "card_bin": None,
            "device_fingerprint": "device_user_0001_1",
            "ip_address": "103.21.58.100",
            "geo_lat": 28.6139,
            "geo_lon": 77.2090,
            "channel": "mobile",
            "timestamp": datetime.utcnow(),
            "metadata": {},
            "enrichment": sample_enriched_context,
        }
        defaults.update(kwargs)
        return TransactionContext(**defaults)
    return _make
