from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress
from app.modules.orders.infrastructure.models.order import Order
from app.modules.reviews.infrastructure.models.review import Review
from app.modules.users.infrastructure.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """Find a single user by unique email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Find a user by primary key."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(self) -> list[User]:
        """Return all user rows."""
        return self.db.query(User).all()

    def create_user(self, user: User) -> User:
        """Persist a new user and return refreshed entity."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID. Returns True if user was deleted, False if not found."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Clean up rows that still reference the user before deleting the user row.
        self.db.query(ShippingAddress).filter(ShippingAddress.user_id == user_id).delete(synchronize_session=False)
        self.db.query(Review).filter(Review.user_id == user_id).delete(synchronize_session=False)
        self.db.query(Order).filter(Order.user_id == user_id).update({Order.user_id: None}, synchronize_session=False)

        self.db.delete(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        return True