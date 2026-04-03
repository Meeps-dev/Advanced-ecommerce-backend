from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderCheckoutInitiated:
    order_id: int
    user_email: str


@dataclass(frozen=True)
class PaymentSucceeded:
    payment_id: int
    order_id: int
    user_id: int
    user_email: str
    total_amount: float


@dataclass(frozen=True)
class OrderShipped:
    order_id: int
    user_id: int
    user_email: str
    status: str = "shipped"
