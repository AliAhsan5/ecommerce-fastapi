from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.address import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
)
from app.services.address_service import (
    create_address,
    delete_address,
    get_owned_address,
    list_addresses,
    update_address,
)


router = APIRouter()


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_address(
    address_data: AddressCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return create_address(
        db=db,
        user=current_user,
        address_data=address_data,
    )


@router.get(
    "",
    response_model=list[AddressResponse],
)
def get_user_addresses(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return list_addresses(
        db=db,
        user=current_user,
    )


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
)
def get_user_address(
    address_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return get_owned_address(
        db=db,
        user=current_user,
        address_id=address_id,
    )


@router.patch(
    "/{address_id}",
    response_model=AddressResponse,
)
def update_user_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return update_address(
        db=db,
        user=current_user,
        address_id=address_id,
        address_data=address_data,
    )


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_address(
    address_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    delete_address(
        db=db,
        user=current_user,
        address_id=address_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )