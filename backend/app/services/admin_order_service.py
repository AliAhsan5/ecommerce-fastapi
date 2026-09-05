from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppException
from app.models.audit_log import AuditLog
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.user import User


ALLOWED_STATUS_TRANSITIONS = {
    "pending": {
        "confirmed",
        "cancelled",
    },
    "confirmed": {
        "processing",
        "cancelled",
    },
    "processing": {
        "shipped",
    },
    "shipped": {
        "delivered",
    },
    "delivered": set(),
    "cancelled": set(),
}


def get_admin_order_detail(
    db: Session,
    order_id: int,
) -> Order:
    order = db.scalar(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(
                Order.status_history
            ),
        )
        .where(
            Order.id == order_id
        )
    )

    if order is None:
        raise AppException(
            message="Order not found.",
            status_code=404,
        )

    return order


def list_admin_orders(
    db: Session,
    page: int,
    page_size: int,
    status: str | None = None,
    user_id: int | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> tuple[list[Order], int]:

    conditions = []

    if status is not None:
        conditions.append(
            Order.status == status
        )

    if user_id is not None:
        conditions.append(
            Order.user_id == user_id
        )

    if created_from is not None:
        conditions.append(
            Order.created_at >= created_from
        )

    if created_to is not None:
        conditions.append(
            Order.created_at <= created_to
        )


    total = db.scalar(
        select(
            func.count(Order.id)
        ).where(
            *conditions
        )
    ) or 0


    orders = list(
        db.scalars(
            select(Order)
            .where(
                *conditions
            )
            .order_by(
                Order.created_at.desc()
            )
            .offset(
                (page - 1)
                * page_size
            )
            .limit(
                page_size
            )
        ).all()
    )

    return orders, total


def update_order_status(
    db: Session,
    admin: User,
    order_id: int,
    new_status: str,
) -> Order:

    order = db.scalar(
        select(Order)
        .where(
            Order.id == order_id
        )
        .with_for_update()
    )

    if order is None:
        raise AppException(
            message="Order not found.",
            status_code=404,
        )


    old_status = order.status


    if new_status == old_status:
        raise AppException(
            message=(
                f"Order is already "
                f"{old_status}."
            ),
            status_code=400,
        )


    allowed_statuses = (
        ALLOWED_STATUS_TRANSITIONS.get(
            old_status,
            set(),
        )
    )


    if new_status not in allowed_statuses:
        raise AppException(
            message=(
                f"Invalid order status "
                f"transition: "
                f"{old_status} -> "
                f"{new_status}."
            ),
            status_code=400,
        )


    try:
        order.status = new_status


        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            changed_by_user_id=admin.id,
        )

        db.add(history)


        audit_log = AuditLog(
            user_id=admin.id,
            action="order_status_changed",
            entity_type="order",
            entity_id=order.id,
            details=(
                f"{old_status} "
                f"-> {new_status}"
            ),
        )

        db.add(audit_log)


        db.commit()


    except Exception:
        db.rollback()
        raise


    return get_admin_order_detail(
        db=db,
        order_id=order.id,
    )