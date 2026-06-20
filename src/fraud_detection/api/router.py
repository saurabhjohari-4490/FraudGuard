"""Top-level API router."""

from fastapi import APIRouter

from fraud_detection.api.v1 import alerts, fraud, health, metrics, mock_control, playground, transactions, users

api_router = APIRouter()

# Health checks (no version prefix)
api_router.include_router(health.router)

# Interactive playground
api_router.include_router(playground.router)

# API v1 endpoints
api_router.include_router(transactions.router)
api_router.include_router(fraud.router)
api_router.include_router(alerts.router)
api_router.include_router(users.router)
api_router.include_router(metrics.router)
api_router.include_router(mock_control.router)
