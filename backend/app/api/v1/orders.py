from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import (
    CheckoutRequest,
    OrderListResponse,
    OrderResponse,
)
from app.services.order_service import (
    checkout,
    get_order_detail,
    list_user_orders,
)


router = APIRouter()


@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def checkout_cart(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return checkout(
        db=db,
        user=current_user,
        checkout_data=checkout_data,
    )


@router.get(
    "",
    response_model=OrderListResponse,
)
def get_my_orders(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    orders, total = list_user_orders(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
    )

    return OrderListResponse(
        items=orders,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_my_order_detail(
    order_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return get_order_detail(
        db=db,
        user=current_user,
        order_id=order_id,
    )