import logging
from typing import List
from sqlalchemy.orm import Session
from app.modules.addresses.api.schemas import AddressCreate
from app.modules.addresses.api.schemas import AddressResponse
from app.modules.addresses.infrastructure.repository import AddressRepository
from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress
from app.core.exceptions import NotFoundError


logger = logging.getLogger(__name__)


class AddressService:
    def __init__(self, db: Session):
        self.db = db
        self.address_repo = AddressRepository(db)
        

    def create_user_address(self, user_id: int, payload: AddressCreate) -> AddressResponse:
        """Create a shipping address for a user."""
        address: ShippingAddress = self.address_repo.create(user_id, payload)
        logger.info(
            "address_created",
            extra={
                "event": "address_created",
                "entity": "address",
                "entity_id": address.id,
                "user_id": user_id,
            },
        )
        return AddressResponse.model_validate(address)



    def list_user_addresses(self, user_id: int) -> List[AddressResponse]:
        """Return all addresses associated with a user."""
        addresses: list[ShippingAddress] = self.address_repo.get_by_user(user_id)
        if not addresses:
            raise NotFoundError(message="No addresses found")
        logger.info(
            "addresses_listed",
            extra={
                "event": "addresses_listed",
                "entity": "address",
                "user_id": user_id,
            },
        )
        return [AddressResponse.model_validate(addr) for addr in addresses]
    

    
    def get_user_address(self, address_id: int) -> AddressResponse:
        """Fetch a single address by identifier."""
        address = self.address_repo.get_by_id(address_id)
        if not address:
            raise NotFoundError("Address not found")
        logger.info(
            "address_fetched",
            extra={
                "event": "address_fetched",
                "entity": "address",
                "entity_id": address_id,
                "user_id": address.user_id,
            },
        )
        return AddressResponse.model_validate(address)
    


    def update_user_address(self, address_id: int, payload: AddressCreate) -> AddressResponse:
        """Update an existing address with request payload fields."""
        address = self.address_repo.get_by_id(address_id)
        if not address:
            raise NotFoundError("Address not found")
        updated_address = self.address_repo.update(address, payload)
        logger.info(
            "address_updated",
            extra={
                "event": "address_updated",
                "entity": "address",
                "entity_id": address_id,
                "user_id": updated_address.user_id,
            },
        )
        return AddressResponse.model_validate(updated_address)

    def delete_user_address(self, address_id: int):
        """Delete a stored address by identifier."""
        address = self.address_repo.get_by_id(address_id)
        if not address:
            raise NotFoundError("Address not found")
        self.address_repo.delete(address)
        logger.info(
            "address_deleted",
            extra={
                "event": "address_deleted",
                "entity": "address",
                "entity_id": address_id,
                "user_id": address.user_id,
            },
        )
