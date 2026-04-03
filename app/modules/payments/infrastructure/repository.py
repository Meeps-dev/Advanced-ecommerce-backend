from typing import Optional
from sqlalchemy.orm import Session
from app.modules.payments.infrastructure.models.payment import Payment


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, order_id: int, amount: float, provider: str) -> Payment:
        payment = Payment(
            order_id=order_id,
            amount=amount,
            provider=provider
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def update_reference(self, payment: Payment, reference: str):
        payment.reference = reference
        self.db.commit()

    def get_by_reference(self, reference: str):
        return self.db.query(Payment).filter(Payment.reference == reference).first()
    

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def update_status(self, payment: Payment, status: str) -> Payment:
        payment.status = status
        self.db.commit()
        self.db.refresh(payment)
        return payment