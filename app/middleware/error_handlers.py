from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import sentry_sdk
from app.core.exceptions import AppError
from app.core.logging import logger


def _build_error_payload(message: str, code: str, details: dict | None = None) -> dict:
    """Return the canonical API error response envelope."""
    payload = {
        "success": False,
        "error": {
            "message": message,
            "code": code,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


def _code_from_status(status_code: int) -> str:
    """Map HTTP status codes to stable application error codes."""
    status_to_code = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
    }
    return status_to_code.get(status_code, "HTTP_ERROR")


async def app_error_handler(request: Request, exc: AppError):
    """Handle domain exceptions that already carry app-specific metadata."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            message=exc.message,
            code=exc.code,
            details=exc.details,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Normalize FastAPI HTTPException objects into the shared error envelope."""
    detail = exc.detail

    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail") or "Request failed"
        code = detail.get("code") or _code_from_status(exc.status_code)
        details = detail.get("details")
    else:
        message = str(detail)
        code = _code_from_status(exc.status_code)
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(message=message, code=code, details=details),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Expose Pydantic validation errors using a consistent API contract."""
    return JSONResponse(
        status_code=422,
        content=_build_error_payload(
            message="Request validation failed",
            code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Capture unexpected failures and hide internals from API consumers."""
    # Forward the original exception to Sentry before returning a sanitized payload.
    sentry_sdk.capture_exception(exc)
    logger.error(
        "UNEXPECTED ERROR: %s %s | Error: %s",
        request.method,
        request.url,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=_build_error_payload(
            message="An internal server error occurred. Please try again later.",
            code="INTERNAL_SERVER_ERROR",
        ),
    )

