"""Mock data generator service - sends transactions to the API at configurable TPS."""

import asyncio
import logging
import signal
import sys

import httpx

from fraud_detection.config import settings
from fraud_detection.mock.transactions import TransactionGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class MockRunner:
    """Continuously generates and sends mock transactions."""

    def __init__(self) -> None:
        self._running = False
        self._generator = TransactionGenerator(
            seed=settings.mock_seed,
            fraud_rate=settings.mock_fraud_rate,
        )
        self._tps = settings.mock_tps
        self._api_url = f"http://fraud-api:{settings.app_port}"
        self._stats = {"sent": 0, "success": 0, "errors": 0}

    async def run(self) -> None:
        """Main loop: generate and send transactions at target TPS."""
        self._running = True
        logger.info(
            f"Mock generator started: TPS={self._tps}, "
            f"fraud_rate={settings.mock_fraud_rate}, seed={settings.mock_seed}"
        )

        interval = 1.0 / self._tps if self._tps > 0 else 1.0

        async with httpx.AsyncClient(base_url=self._api_url, timeout=10.0) as client:
            while self._running:
                try:
                    txn = self._generator.generate_normal()

                    # Inject fraud based on rate
                    import random
                    if random.random() < settings.mock_fraud_rate:
                        fraud_txns = self._generator.generate_fraud()
                        if fraud_txns:
                            txn = fraud_txns[0]

                    response = await client.post(
                        "/api/v1/transactions",
                        json=txn.model_dump(mode="json"),
                    )
                    self._stats["sent"] += 1

                    if response.status_code == 201:
                        self._stats["success"] += 1
                    else:
                        self._stats["errors"] += 1

                    # Log progress every 100 transactions
                    if self._stats["sent"] % 100 == 0:
                        logger.info(
                            f"Progress: sent={self._stats['sent']}, "
                            f"success={self._stats['success']}, "
                            f"errors={self._stats['errors']}"
                        )

                except httpx.RequestError as e:
                    self._stats["errors"] += 1
                    logger.warning(f"Request failed: {e}")
                    await asyncio.sleep(1)  # Back off on errors

                await asyncio.sleep(interval)

    def stop(self) -> None:
        """Gracefully stop the generator."""
        self._running = False
        logger.info(f"Mock generator stopped. Final stats: {self._stats}")


async def main() -> None:
    runner = MockRunner()

    def handle_signal(sig: int, frame: object) -> None:
        runner.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())
