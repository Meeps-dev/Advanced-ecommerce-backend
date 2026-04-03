from sqlalchemy.orm import Session
from app.modules.auth.infrastructure.models.refresh_token import RefreshToken
from app.core.security import hash_token


class RefreshTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_token(self, token: RefreshToken):
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def delete_token(self, token: RefreshToken):
        self.db.delete(token)
        self.db.commit()

    def delete_tokens_by_user(self, user_id: int) -> int:
        deleted_count = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count

    def find_valid_token(self, raw_token: str) -> RefreshToken | None:
        hashed = hash_token(raw_token)

        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == hashed)
            .first()
        )