from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailBase(BaseModel):
    """Common fields for every background email."""

    recipient: EmailStr
    subject: str
    template_name: Optional[str] = None  # For future HTML templates


class OrderConfirmationPayload(EmailBase):
    """Data specifically needed for the confirmation email."""

    order_id: int
    user_name: str
    total_amount: float
    items_count: int


class ShippingUpdatePayload(EmailBase):
    """Data specifically needed for shipping notifications."""

    order_id: int
    status: str  # e.g., "shipped", "delivered"
    tracking_number: Optional[str] = None


class PasswordResetPayload(EmailBase):
    """Data for security emails."""

    reset_token: str
    expiry_minutes: int = 15
