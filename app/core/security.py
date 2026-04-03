import jwt
import secrets
import hashlib
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto" )


def hash_password(password: str) -> str:
    """Hash a plain-text password with the configured Argon2 context."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """Create a short-lived access token carrying the provided claims."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh token with an explicit token type claim."""
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )


def hash_token(token: str):
    """Hash refresh tokens before persisting them to storage."""
    return pwd_context.hash(token)


def verify_token_hash(plain_token: str, hashed_token: str):
    """Compare an incoming refresh token against a stored token hash."""
    return pwd_context.verify(plain_token, hashed_token)


def create_secure_token() -> str:
    """Generate a URL-safe random token for one-time password reset use."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """Create a deterministic SHA-256 digest for password reset token lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()