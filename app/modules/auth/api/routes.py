from fastapi import APIRouter, Depends, Request
from app.core.exceptions import UnauthorizedError
from app.modules.auth.application.login_rate_limiter import LoginRateLimiter
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.api.schemas import (
    MessageResponse as AuthMessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
)
from app.modules.users.api.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    RefreshRequest
)

from app.modules.auth.application.service import AuthService
from app.dependencies.services import get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_login_rate_limiter() -> LoginRateLimiter:
    return LoginRateLimiter()

def _extract_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


# 1. Register with UserResponse to hide the password
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    return service.register_user(
        email=user.email,
        password=user.password,
        full_name=user.full_name
    )


# 2. Login using TokenResponse (The standard JWT output)
@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
    limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
):
    ip_address = _extract_client_ip(request)
    limiter.ensure_allowed(ip_address)

    try:
        tokens = service.login_user(form_data.username, form_data.password)
    except UnauthorizedError:
        limiter.record_failure(ip_address)
        raise

    limiter.reset(ip_address)
    return tokens




# 3. Refresh & Logout using your RefreshRequest schema
@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    return service.rotate_refresh_token(data.refresh_token)


@router.post("/logout", response_model=AuthMessageResponse)
def logout(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    return service.logout_user(data.refresh_token)


@router.post("/password-reset/request", response_model=AuthMessageResponse)
def request_password_reset(
    payload: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.request_password_reset(payload.email)


@router.post("/password-reset/confirm", response_model=AuthMessageResponse)
def confirm_password_reset(
    payload: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
):
    return service.reset_password(payload.token, payload.new_password)