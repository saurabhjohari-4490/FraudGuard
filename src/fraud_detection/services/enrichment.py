"""Feature Enrichment Service - parallel Redis lookups with timeout."""

import asyncio
import logging
import time
from dataclasses import dataclass, field

from fraud_detection.cache.device_profile import DeviceProfileCache
from fraud_detection.cache.user_profile import UserProfileCache
from fraud_detection.cache.velocity import VelocityCounter
from fraud_detection.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EnrichedContext:
    """Enriched transaction context with all features."""

    # Velocity features
    velocity_1m: int = 0
    velocity_5m: int = 0
    velocity_1h: int = 0
    velocity_24h: int = 0

    # User profile features
    user_avg_amount: float = 0.0
    user_txn_count: int = 0
    user_typical_merchants: list[str] = field(default_factory=list)
    user_typical_geo_regions: list[str] = field(default_factory=list)
    user_risk_level: str = "unknown"

    # Device features
    device_user_count: int = 0
    device_is_emulator: bool = False
    device_is_rooted: bool = False
    device_first_seen: float = 0.0
    device_risk_score: float = 0.0

    # Enrichment metadata
    enrichment_time_ms: float = 0.0
    partial: bool = False


class FeatureEnrichmentService:
    """Enriches transactions with velocity, user, and device features."""

    def __init__(
        self,
        velocity: VelocityCounter,
        user_cache: UserProfileCache,
        device_cache: DeviceProfileCache,
    ) -> None:
        self._velocity = velocity
        self._user_cache = user_cache
        self._device_cache = device_cache

    async def enrich(
        self, user_id: str, device_fingerprint: str | None, amount: float
    ) -> EnrichedContext:
        """Enrich a transaction with all available features.

        Runs all lookups in parallel with a hard timeout.
        Falls back to defaults for any timed-out or failed lookups.
        """
        start = time.perf_counter()
        timeout = settings.enrichment_timeout_ms / 1000.0
        context = EnrichedContext()

        # Run all enrichment tasks in parallel
        velocity_task = self._enrich_velocity(user_id)
        user_task = self._enrich_user(user_id)
        device_task = self._enrich_device(device_fingerprint)

        results = await asyncio.gather(
            asyncio.wait_for(velocity_task, timeout=timeout),
            asyncio.wait_for(user_task, timeout=timeout),
            asyncio.wait_for(device_task, timeout=timeout),
            return_exceptions=True,
        )

        # Apply velocity results
        if isinstance(results[0], dict):
            context.velocity_1m = results[0].get("1m", 0)
            context.velocity_5m = results[0].get("5m", 0)
            context.velocity_1h = results[0].get("1h", 0)
            context.velocity_24h = results[0].get("24h", 0)
        else:
            context.partial = True
            logger.warning(f"Velocity enrichment failed: {results[0]}")

        # Apply user profile results
        if isinstance(results[1], dict):
            context.user_avg_amount = results[1].get("avg_amount", 0)
            context.user_txn_count = results[1].get("txn_count", 0)
            context.user_typical_merchants = results[1].get("typical_merchants", [])
            context.user_typical_geo_regions = results[1].get("typical_geo_regions", [])
            context.user_risk_level = results[1].get("risk_level", "unknown")
        else:
            context.partial = True
            logger.warning(f"User profile enrichment failed: {results[1]}")

        # Apply device results
        if isinstance(results[2], dict):
            context.device_user_count = results[2].get("user_count", 0)
            context.device_is_emulator = results[2].get("is_emulator", False)
            context.device_is_rooted = results[2].get("is_rooted", False)
            context.device_first_seen = results[2].get("first_seen", 0)
            context.device_risk_score = results[2].get("risk_score", 0)
        else:
            context.partial = True
            logger.warning(f"Device enrichment failed: {results[2]}")

        context.enrichment_time_ms = (time.perf_counter() - start) * 1000

        # Record velocity (always — we count all transactions for burst detection)
        try:
            await self._velocity.record(user_id, amount)
        except Exception as e:
            logger.warning(f"Failed to record velocity: {e}")

        return context

    async def _enrich_velocity(self, user_id: str) -> dict:
        return await self._velocity.get_velocity_profile(user_id)

    async def _enrich_user(self, user_id: str) -> dict:
        profile = await self._user_cache.get(user_id)
        return profile or {"avg_amount": 0, "txn_count": 0, "typical_merchants": [], "risk_level": "unknown"}

    async def _enrich_device(self, fingerprint: str | None) -> dict:
        if not fingerprint:
            return {"user_count": 0, "is_emulator": False, "is_rooted": False, "first_seen": 0, "risk_score": 0}
        profile = await self._device_cache.get(fingerprint)
        return profile or {"user_count": 0, "is_emulator": False, "is_rooted": False, "first_seen": 0, "risk_score": 0}

    async def update_profile_on_approve(
        self, user_id: str, device_fingerprint: str | None, amount: float, merchant_id: str
    ) -> None:
        """Update user/device profiles ONLY when transaction is approved.

        Fraudulent transactions (block/escalate/verify) must NOT alter the
        user's baseline profile — otherwise a single ₹2,000,000 fraud txn
        would permanently inflate the user's avg_amount, making future fraud
        at ₹50,000 look "normal" by comparison.

        Velocity counters are updated separately (always) since they track
        ALL transaction patterns regardless of legitimacy.
        """
        try:
            await asyncio.gather(
                self._user_cache.update_on_transaction(user_id, amount, merchant_id),
                self._device_cache.record_usage(device_fingerprint or "", user_id),
                return_exceptions=True,
            )
        except Exception as e:
            logger.warning(f"Failed to update profile caches: {e}")
