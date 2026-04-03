from fastapi import APIRouter, Depends, Header, Request

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_payment_service
from app.core.exceptions import UnauthorizedError

from app.modules.payments.api.schemas import (
    PaymentResponse,
    PaymentVerifyRequest,
)

from app.modules.payments.application.service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])



@router.post("/webhook")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(None),
    service: PaymentService = Depends(get_payment_service)
):
    body = await request.body()

    if not service.verify_webhook_signature(body, x_paystack_signature):
        print("Unauthorized webhook attempt blocked")
        raise UnauthorizedError("Invalid signature")

    processed = service.handle_webhook(body, x_paystack_signature)
    if not processed:
        return {"status": "ignored"}

    return {"status": "success"}


@router.post("/verify", response_model=PaymentResponse)
def verify_payment(
    payload: PaymentVerifyRequest,
    service: PaymentService = Depends(get_payment_service),
    current_user=Depends(get_current_user),
):
    payment = service.verify_payment_by_reference(payload.reference)
    return payment