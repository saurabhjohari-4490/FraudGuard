"""Mock generator control API - start/stop/status."""

import asyncio
import logging
import random

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from fraud_detection.config import settings
from fraud_detection.mock.transactions import TransactionGenerator

router = APIRouter(prefix="/api/v1/mock", tags=["mock"])
logger = logging.getLogger(__name__)


class MockStatus(BaseModel):
    enabled: bool
    tps: int
    fraud_rate: float
    stats: dict


class MockStartRequest(BaseModel):
    tps: int | None = None
    fraud_rate: float | None = None


# Module-level state for the background mock generator
_mock_task: asyncio.Task | None = None
_mock_running = False
_mock_tps = settings.mock_tps
_mock_fraud_rate = settings.mock_fraud_rate
_mock_stats = {"sent": 0, "success": 0, "errors": 0}


async def _mock_loop() -> None:
    """Background task that generates and sends mock transactions."""
    global _mock_running, _mock_stats

    generator = TransactionGenerator(seed=settings.mock_seed, fraud_rate=_mock_fraud_rate)
    interval = 1.0 / _mock_tps if _mock_tps > 0 else 1.0
    api_url = f"http://localhost:{settings.app_port}"

    logger.info(f"Mock generator started: TPS={_mock_tps}, fraud_rate={_mock_fraud_rate}")

    async with httpx.AsyncClient(base_url=api_url, timeout=10.0) as client:
        while _mock_running:
            try:
                txn = generator.generate_normal()

                if random.random() < _mock_fraud_rate:
                    fraud_txns = generator.generate_fraud()
                    if fraud_txns:
                        txn = fraud_txns[0]

                response = await client.post(
                    "/api/v1/transactions",
                    json=txn.model_dump(mode="json"),
                )
                _mock_stats["sent"] += 1

                if response.status_code == 201:
                    _mock_stats["success"] += 1
                else:
                    _mock_stats["errors"] += 1

                if _mock_stats["sent"] % 100 == 0:
                    logger.info(
                        f"Mock progress: sent={_mock_stats['sent']}, "
                        f"success={_mock_stats['success']}, errors={_mock_stats['errors']}"
                    )

            except httpx.RequestError as e:
                _mock_stats["errors"] += 1
                logger.warning(f"Mock request failed: {e}")
                await asyncio.sleep(1)

            await asyncio.sleep(interval)

    logger.info(f"Mock generator stopped. Stats: {_mock_stats}")


async def start_mock(tps: int | None = None, fraud_rate: float | None = None) -> None:
    """Start the mock generator background task."""
    global _mock_task, _mock_running, _mock_tps, _mock_fraud_rate, _mock_stats

    if _mock_running:
        return

    if tps is not None:
        _mock_tps = tps
    if fraud_rate is not None:
        _mock_fraud_rate = fraud_rate

    _mock_running = True
    _mock_stats = {"sent": 0, "success": 0, "errors": 0}
    _mock_task = asyncio.create_task(_mock_loop())


async def stop_mock() -> None:
    """Stop the mock generator background task."""
    global _mock_task, _mock_running

    if not _mock_running:
        return

    _mock_running = False
    if _mock_task:
        await asyncio.wait_for(_mock_task, timeout=5.0)
        _mock_task = None


@router.get("/status", response_model=MockStatus)
async def mock_status() -> MockStatus:
    """Get mock generator status."""
    return MockStatus(
        enabled=_mock_running,
        tps=_mock_tps,
        fraud_rate=_mock_fraud_rate,
        stats=_mock_stats,
    )


@router.post("/start", response_model=MockStatus)
async def mock_start(body: MockStartRequest | None = None) -> MockStatus:
    """Start the mock transaction generator."""
    tps = body.tps if body else None
    fraud_rate = body.fraud_rate if body else None
    await start_mock(tps=tps, fraud_rate=fraud_rate)
    return MockStatus(
        enabled=_mock_running,
        tps=_mock_tps,
        fraud_rate=_mock_fraud_rate,
        stats=_mock_stats,
    )


@router.post("/stop", response_model=MockStatus)
async def mock_stop() -> MockStatus:
    """Stop the mock transaction generator."""
    await stop_mock()
    return MockStatus(
        enabled=_mock_running,
        tps=_mock_tps,
        fraud_rate=_mock_fraud_rate,
        stats=_mock_stats,
    )
