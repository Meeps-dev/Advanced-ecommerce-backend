from pydantic import BaseModel, ConfigDict

class PaymentVerifyRequest(BaseModel):
    reference: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str

    model_config = ConfigDict(from_attributes=True)