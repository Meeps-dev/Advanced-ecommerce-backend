from typing import Any


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "BAD_REQUEST",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


class BadRequestError(AppError):
    def __init__(self, message: str = "Invalid request", code: str = "BAD_REQUEST"):
        super().__init__(message=message, status_code=400, code=code)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401, code="UNAUTHORIZED")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403, code="FORBIDDEN")


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource", message: str | None = None):
        resolved_message = message or f"{resource} not found"
        super().__init__(message=resolved_message, status_code=404, code="NOT_FOUND")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", code: str = "CONFLICT"):
        super().__init__(message=message, status_code=409, code=code)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=422, code="VALIDATION_ERROR")


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service error", code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(message=message, status_code=502, code=code)


class TooManyRequestsError(AppError):
    def __init__(
        self,
        message: str = "Too many login attempts from this IP. Try again later.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            code="TOO_MANY_REQUESTS",
            details=details,
        )


class ResourceNotFoundError(NotFoundError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(resource=resource)


class InsufficientStockError(ConflictError):
    def __init__(self, product_name: str):
        super().__init__(
            message=f"Not enough stock for {product_name}",
            code="OUT_OF_STOCK",
        )


class PaymentGatewayError(ExternalServiceError):
    def __init__(self, message: str = "Payment provider error"):
        super().__init__(message=message, code="PAYMENT_GATEWAY_ERROR")
