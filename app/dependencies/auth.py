from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.modules.users.infrastructure.models.user import User
from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.shared.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):
    """Resolve and validate the authenticated user from a bearer JWT."""

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid authentication credentials")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")

    return user


def admin_required(current_user: User = Depends(get_current_user)):
    """Guard dependency that allows only admin users."""
    if current_user.role != UserRole.admin:
        raise ForbiddenError("Admin access required")
    return current_user
