import time
import uuid
import os
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.api.router import api_router
from app.core.config import settings
from app.modules.events.event_registry import register_domain_event_listeners
from app.core.exceptions import AppError
from app.core.logging import logger
from app.middleware.error_handlers import (
    app_error_handler,
    http_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Emit startup diagnostics and report observability configuration."""
    register_domain_event_listeners()
    logger.info(
        "api_startup",
        extra={
            "request_id": "-",
            "method": "-",
            "path": "-",
            "status_code": 0,
            "latency_ms": 0,
        },
    )
    if settings.sentry_dsn:
        logger.info(
            "sentry_enabled",
            extra={
                "request_id": "-",
                "method": "-",
                "path": "-",
                "status_code": 0,
                "latency_ms": 0,
            },
        )
    else:
        logger.warning(
            "sentry_disabled_missing_dsn",
            extra={
                "request_id": "-",
                "method": "-",
                "path": "-",
                "status_code": 0,
                "latency_ms": 0,
            },
        )
    yield 


app = FastAPI(title="Meeps Store API", version="1.0.0", lifespan=lifespan)

# --- Sentry Initialization ---
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
    )

# --- Middleware for Request Logging ---

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log each request with latency and a synthetic request id."""
    start = time.perf_counter()
    method = request.method
    path = request.url.path
    request_id = str(uuid.uuid4())
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        # Keep logging in a finally block so failed requests are still measured.
        duration = time.perf_counter() - start
        latency_ms = round(duration * 1000, 2)

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "latency_ms": latency_ms,
            },
        )


# --- Exception Handlers ---

@app.exception_handler(AppError)
async def custom_app_exception_handler(request: Request, exc: AppError):
    return await app_error_handler(request, exc)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def custom_unhandled_exception_handler(request: Request, exc: Exception):
    return await unhandled_exception_handler(request, exc)

app.include_router(api_router, prefix="/api/v1")

