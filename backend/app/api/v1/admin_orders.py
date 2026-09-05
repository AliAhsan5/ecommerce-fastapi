from datetime import datetime
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_order import (
    OrderStatusUpdate,
)
from app.schemas.order import (
    OrderListResponse,
    OrderResponse,
)
from app.services.admin_order_service import (
    get_admin_order_detail,
    list_admin_orders,
    update_order_status,
)


router = APIRouter()


@router.get(
    "",
    response_model=OrderListResponse,
)
def get_all_orders(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    status: Literal[
        "pending",
        "confirmed",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    ] | None = None,
    user_id: int | None = Query(
        default=None,
        gt=0,
    ),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    orders, total = list_admin_orders(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        user_id=user_id,
        created_from=created_from,
        created_to=created_to,
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
def get_order_detail(
    order_id: int,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return get_admin_order_detail(
        db=db,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def change_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_order_status(
        db=db,
        admin=current_admin,
        order_id=order_id,
        new_status=status_data.status,
    )