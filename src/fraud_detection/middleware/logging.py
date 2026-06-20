"""Structured JSON logging middleware."""

import logging
import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from fraud_detection.config import settings
from fraud_detection.middleware.correlation import correlation_id_ctx, request_id_ctx


def configure_logging() -> None:
    """Configure structlog for JSON output in production, pretty-print in dev."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.is_production:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.app_log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger = structlog.get_logger()
        start = time.perf_counter()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id_ctx.get(),
            correlation_id=correlation_id_ctx.get(),
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        await logger.ainfo(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        return response
