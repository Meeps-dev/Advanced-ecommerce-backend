from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    full_name: str
    address_line1: str
    city: str
    state: str
    postal_code: str
    country: str


class AddressResponse(BaseModel):
    id: int
    full_name: str
    address_line1: str
    city: str
    state: str
    postal_code: str
    country: str

    model_config = ConfigDict(from_attributes=True)