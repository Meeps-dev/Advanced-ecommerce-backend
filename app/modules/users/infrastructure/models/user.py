from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum
from sqlalchemy.orm import relationship 
from app.db.base import Base
from app.shared.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    orders = relationship("Order", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
