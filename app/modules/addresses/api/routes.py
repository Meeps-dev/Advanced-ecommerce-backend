from typing import List
from fastapi import APIRouter, Depends
from app.dependencies.services import get_address_service
from app.modules.addresses.api.schemas import AddressCreate, AddressResponse
from app.dependencies.auth import get_current_user
from app.modules.users.infrastructure.models.user import User
from app.modules.addresses.application.service import AddressService


router = APIRouter(prefix="/addresses", tags=["Addresses"])




@router.post("/", response_model=AddressResponse)
def create_address(
    payload: AddressCreate,
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    """
    Create a new shipping address for the current user.
    """
    return service.create_user_address(current_user.id, payload)


@router.get("/", response_model=List[AddressResponse])
def list_addresses(
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    """
    List all shipping addresses of the current user.
    """
    return service.list_user_addresses(current_user.id)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    """
    Get a specific shipping address of the current user.
    """
    return service.get_user_address(address_id)

    

@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    payload: AddressCreate,
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    """
    Update an existing shipping address of the current user.
    """
    return service.update_user_address(address_id, payload)


@router.delete("/{address_id}")    
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    service: AddressService = Depends(get_address_service),
):
    """
    Delete a shipping address of the current user.
    """
    return service.delete_user_address(address_id)