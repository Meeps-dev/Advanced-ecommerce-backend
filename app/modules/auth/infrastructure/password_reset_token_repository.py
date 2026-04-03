from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_reset_token
from app.modules.auth.infrastructure.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, token: PasswordResetToken):
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def find_valid_token(self, raw_token: str) -> PasswordResetToken | None:
        hashed = hash_reset_token(raw_token)
        now = datetime.now(timezone.utc)
        return (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == hashed,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .first()
        )

    def mark_used(self, token: PasswordResetToken):
        token.used_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(token)
        return token

    def delete_token(self, token: PasswordResetToken):
        self.db.delete(token)
        self.db.commit()

    def delete_tokens_by_user(self, user_id: int) -> int:
        deleted_count = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count
