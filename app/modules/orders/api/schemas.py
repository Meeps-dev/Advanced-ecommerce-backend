from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class CheckoutResponse(BaseModel):
    order_id: int
    status: OrderStatus
    checkout_url: str
    total: float