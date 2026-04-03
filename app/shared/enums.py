from enum import Enum

# (EVENT DRIVEN) Enums for user roles, order status, and payment status

class UserRole(str, Enum):
    admin = "admin"
    customer = "customer"


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    successful = "successful"
    failed = "failed"
