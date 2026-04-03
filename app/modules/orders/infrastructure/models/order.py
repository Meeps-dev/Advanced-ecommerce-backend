from sqlalchemy import Column, Float, Integer, ForeignKey, DateTime, Enum
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.shared.enums import OrderStatus
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    
    # NEW: Store the snapshot of the total cost
    total_price = Column(Float, default=0.0) 

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

    