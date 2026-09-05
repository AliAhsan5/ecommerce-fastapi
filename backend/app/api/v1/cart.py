from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse,
)
from app.schemas.user import MessageResponse
from app.services.cart_service import (
    add_cart_item,
    clear_cart,
    get_user_cart,
    remove_cart_item,
    update_cart_item,
)


router = APIRouter()


@router.get(
    "",
    response_model=CartResponse,
)
def get_cart(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return get_user_cart(
        db=db,
        user=current_user,
    )


@router.post(
    "/items",
    response_model=CartResponse,
)
def add_item(
    item_data: CartItemAdd,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return add_cart_item(
        db=db,
        user=current_user,
        item_data=item_data,
    )


@router.patch(
    "/items/{item_id}",
    response_model=CartResponse,
)
def update_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return update_cart_item(
        db=db,
        user=current_user,
        item_id=item_id,
        item_data=item_data,
    )


@router.delete(
    "/items/{item_id}",
    response_model=MessageResponse,
)
def remove_item(
    item_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    remove_cart_item(
        db=db,
        user=current_user,
        item_id=item_id,
    )

    return MessageResponse(
        message="Cart item removed successfully."
    )


@router.delete(
    "/items",
    response_model=MessageResponse,
)
def clear_all_items(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    clear_cart(
        db=db,
        user=current_user,
    )

    return MessageResponse(
        message="Cart cleared successfully."
    )