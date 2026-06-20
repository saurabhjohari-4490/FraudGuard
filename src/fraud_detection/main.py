"""FastAPI application factory."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fraud_detection.cache.pool import close_redis, init_redis
from fraud_detection.config import settings
from fraud_detection.db.engine import close_db, init_db
from fraud_detection.db.migrate import run_migrations
from fraud_detection.middleware.correlation import CorrelationMiddleware
from fraud_detection.middleware.logging import StructuredLoggingMiddleware, configure_logging
from fraud_detection.middleware.timing import TimingMiddleware
from fraud_detection.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    configure_logging()
    await run_migrations()
    await init_db()
    await init_redis()

    # Auto-start mock generator if MOCK_ENABLED=true
    if settings.mock_enabled:
        from fraud_detection.api.v1.mock_control import start_mock
        await start_mock()

    yield

    # Stop mock generator if running
    from fraud_detection.api.v1.mock_control import stop_mock
    await stop_mock()

    await close_redis()
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Fraud Detection Platform",
        description="AI-Powered Fraud Detection API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters: outermost first)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)

    # Routes
    app.include_router(api_router)

    return app


app = create_app()
