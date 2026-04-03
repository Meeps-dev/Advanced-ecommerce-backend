from sqlalchemy import Column, Integer, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.shared.enums import PaymentStatus

class Payment(Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"))

    amount = Column(Integer)

    provider = Column(String)

    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)

    reference = Column(String)

    order = relationship("Order")

    