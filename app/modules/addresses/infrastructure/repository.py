from typing import List
from sqlalchemy.orm import Session
from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress
from app.modules.addresses.api.schemas import AddressCreate


class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, payload: AddressCreate) -> ShippingAddress:
        """Persist and return a new shipping address row."""
        address = ShippingAddress(user_id=user_id, **payload.model_dump())
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address

    def get_by_user(self, user_id: int) -> List[ShippingAddress]:
        """List all shipping addresses for a user."""
        return (
            self.db.query(ShippingAddress)
            .filter(ShippingAddress.user_id == user_id)
            .all()
        )

    def update(self, address: ShippingAddress, payload: AddressCreate) -> ShippingAddress:
        """Apply payload fields to an existing address entity."""
        for field, value in payload.model_dump().items():
            setattr(address, field, value)
        self.db.commit()
        self.db.refresh(address)
        return address   
    
    def get_by_id(self, address_id: int) -> ShippingAddress:
        return self.db.query(ShippingAddress).filter(ShippingAddress.id == address_id).first()
    
    def delete(self, address: ShippingAddress):
        self.db.delete(address)
        self.db.commit()


       