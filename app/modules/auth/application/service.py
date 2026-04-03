import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.modules.users.infrastructure.models.user import User
from app.shared.enums import UserRole
from app.modules.auth.infrastructure.models.refresh_token import RefreshToken
from app.modules.auth.infrastructure.models.password_reset_token import PasswordResetToken

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    create_secure_token,
    hash_reset_token,
)

from app.modules.users.infrastructure.repository import UserRepository
from app.modules.auth.infrastructure.refresh_token_repository import RefreshTokenRepository
from app.modules.auth.infrastructure.password_reset_token_repository import PasswordResetTokenRepository
from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.config import settings
from app.tasks.email_tasks import send_password_reset_email, send_welcome_email


REFRESH_TOKEN_EXPIRE_DAYS: int = 7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.password_reset_repo = PasswordResetTokenRepository(db)

    def register_user(self, email: str, password: str, full_name: str) -> User:
        """Register a customer account and trigger welcome-email delivery."""

        existing_user = self.user_repo.get_user_by_email(email)

        if existing_user:
            raise ConflictError("Email already registered")

        new_user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole.customer
        )

        created_user = self.user_repo.create_user(new_user)
        send_welcome_email.delay(created_user.email, created_user.full_name or created_user.email)
        logger.info(
            "auth_user_registered",
            extra={
                "event": "user_registered",
                "entity": "user",
                "entity_id": created_user.id,
                "user_id": created_user.id,
            },
        )

        return created_user

    def login_user(self, email: str, password: str):
        """Authenticate a user and issue access/refresh tokens."""

        user = self.user_repo.get_user_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        access_token = create_access_token({"sub": str(user.id)})

        # Persist only a hash of the refresh token so raw tokens are never stored.
        raw_refresh = create_refresh_token({"sub": str(user.id)})
        hashed_refresh = hash_token(raw_refresh)

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        self.refresh_repo.create_token(refresh_token)
        logger.info(
            "auth_login_succeeded",
            extra={
                "event": "user_logged_in",
                "entity": "user",
                "entity_id": user.id,
                "user_id": user.id,
            },
        )

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer"
        }

    def rotate_refresh_token(self, raw_refresh_token: str):
        """Rotate refresh credentials by revoking old token and issuing a new pair."""

        token = self.refresh_repo.find_valid_token(raw_refresh_token)

        if not token:
            raise UnauthorizedError("Invalid refresh token")

        if token.expires_at < datetime.now(timezone.utc):
            self.refresh_repo.delete_token(token)
            raise UnauthorizedError("Refresh token expired")

        user = token.user

        # Delete first so replay attempts on the old token fail immediately.
        self.refresh_repo.delete_token(token)

        new_access = create_access_token({"sub": str(user.id)})
        new_raw_refresh = create_refresh_token({"sub": str(user.id)})
        new_hash = hash_token(new_raw_refresh)

        new_token = RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        self.refresh_repo.create_token(new_token)
        logger.info(
            "auth_refresh_rotated",
            extra={
                "event": "refresh_token_rotated",
                "entity": "user",
                "entity_id": user.id,
                "user_id": user.id,
            },
        )

        return {
            "access_token": new_access,
            "refresh_token": new_raw_refresh,
            "token_type": "bearer"
        }

    def logout_user(self, raw_refresh_token: str):
        """Invalidate an existing refresh token and end the session."""

        token = self.refresh_repo.find_valid_token(raw_refresh_token)

        if not token:
            raise BadRequestError("Invalid refresh token")

        user_id = token.user_id
        self.refresh_repo.delete_token(token)
        logger.info(
            "auth_logout_succeeded",
            extra={
                "event": "user_logged_out",
                "entity": "user",
                "entity_id": user_id,
                "user_id": user_id,
            },
        )

        return {"message": "Successfully logged out"}

    def request_password_reset(self, email: str) -> dict:
        """Create a one-time reset token and email the reset link if the account exists."""
        user = self.user_repo.get_user_by_email(email)
        if not user:
            # Avoid account enumeration.
            return {"message": "If the account exists, a reset link has been sent."}

        self.password_reset_repo.delete_tokens_by_user(user.id)

        raw_token = create_secure_token()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(raw_token),
            expires_at=datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
        self.password_reset_repo.create_token(reset_token)

        reset_url = f"{settings.password_reset_frontend_url}?token={raw_token}"
        send_password_reset_email.delay(
            user_email=user.email,
            full_name=user.full_name or user.email,
            reset_url=reset_url,
        )

        logger.info(
            "auth_password_reset_requested",
            extra={
                "event": "password_reset_requested",
                "entity": "user",
                "entity_id": user.id,
                "user_id": user.id,
            },
        )

        return {"message": "If the account exists, a reset link has been sent."}

    def reset_password(self, token: str, new_password: str) -> dict:
        """Consume a password reset token and update the user password once."""
        reset_token = self.password_reset_repo.find_valid_token(token)
        if not reset_token:
            raise BadRequestError("Invalid or expired password reset token")

        user = reset_token.user
        if not user:
            raise BadRequestError("Invalid password reset token")

        user.password_hash = hash_password(new_password)
        self.db.add(user)
        self.db.commit()

        self.password_reset_repo.delete_token(reset_token)
        self.refresh_repo.delete_tokens_by_user(user.id)

        logger.info(
            "auth_password_reset_completed",
            extra={
                "event": "password_reset_completed",
                "entity": "user",
                "entity_id": user.id,
                "user_id": user.id,
            },
        )

        return {"message": "Password updated successfully"}