import logging
from redis import Redis
from app.core.config import settings
from app.core.exceptions import TooManyRequestsError


logger = logging.getLogger(__name__)

class LoginRateLimiter:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self.max_attempts = settings.login_rate_limit_max_attempts
        self.window_seconds = settings.login_rate_limit_window_minutes * 60



    def _key(self, ip_address: str) -> str:
        return f"auth:login:fail:{ip_address}"



    def ensure_allowed(self, ip_address: str) -> None:
        """Raise when an IP has exceeded the configured failure threshold."""
        key = self._key(ip_address)
        attempts = self.redis.get(key)
        if attempts and int(attempts) >= self.max_attempts:
            # Redis may return -1/-2; clamp to a safe non-negative retry hint.
            ttl = max(self.redis.ttl(key), 0)
            logger.warning(
                "login_rate_limited",
                extra={
                    "event": "login_rate_limited",
                    "entity": "auth",
                },
            )
            raise TooManyRequestsError(
                message="Too many login attempts from this IP. Try again later.",
                details={"retry_after_seconds": ttl},
            )
        


    def record_failure(self, ip_address: str) -> None:
        """Record a failed login attempt within a fixed expiry window."""
        key = self._key(ip_address)
        # INCR is atomic, making this safe under concurrent login attempts.
        attempts = self.redis.incr(key)
        if attempts == 1:
            self.redis.expire(key, self.window_seconds)
        logger.info(
            "login_failure_recorded",
            extra={
                "event": "login_failure_recorded",
                "entity": "auth",
            },
        )



    def reset(self, ip_address: str) -> None:
        """Clear failure counters after successful authentication."""
        self.redis.delete(self._key(ip_address))
        logger.info(
            "login_rate_limit_reset",
            extra={
                "event": "login_rate_limit_reset",
                "entity": "auth",
            },
        )