"""Dependency injection container for FastAPI."""

from functools import lru_cache

from fraud_detection.cache.device_profile import DeviceProfileCache
from fraud_detection.cache.pool import get_redis
from fraud_detection.cache.user_profile import UserProfileCache
from fraud_detection.cache.velocity import VelocityCounter
from fraud_detection.services.enrichment import FeatureEnrichmentService


@lru_cache
def get_velocity_counter() -> VelocityCounter:
    return VelocityCounter(get_redis())


@lru_cache
def get_user_profile_cache() -> UserProfileCache:
    return UserProfileCache(get_redis())


@lru_cache
def get_device_profile_cache() -> DeviceProfileCache:
    return DeviceProfileCache(get_redis())


@lru_cache
def get_enrichment_service() -> FeatureEnrichmentService:
    return FeatureEnrichmentService(
        velocity=get_velocity_counter(),
        user_cache=get_user_profile_cache(),
        device_cache=get_device_profile_cache(),
    )
