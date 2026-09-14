from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User


def make_safe_value(
    value,
):
    """
    Convert ORM values into JSON-safe
    values for AI tools.
    """

    if isinstance(
        value,
        Decimal,
    ):
        return str(value)

    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    return value


def get_first_attribute(
    obj,
    *names,
):
    """
    Safely support slightly different
    model field names without crashing.
    """

    for name in names:

        if hasattr(
            obj,
            name,
        ):
            return getattr(
                obj,
                name
            )

    return None


def build_order_tool_data(
    order: Order,
) -> dict:
    """
    Build safe order information.

    Important:
    user_id is deliberately NOT returned.
    """

    total = get_first_attribute(
        order,
        "total",
        "total_amount",
        "grand_total",
    )

    subtotal = get_first_attribute(
        order,
        "subtotal",
        "sub_total",
    )

    shipping = get_first_attribute(
        order,
        "shipping",
        "shipping_amount",
        "shipping_cost",
    )

    payment_method = (
        get_first_attribute(
            order,
            "payment_method",
            "payment_type",
        )
    )

    return {
        "order_id": order.id,

        "status": make_safe_value(
            get_first_attribute(
                order,
                "status",
            )
        ),

        "subtotal": make_safe_value(
            subtotal
        ),

        "shipping": make_safe_value(
            shipping
        ),

        "total": make_safe_value(
            total
        ),

        "payment_method": (
            make_safe_value(
                payment_method
            )
        ),

        "created_at": make_safe_value(
            get_first_attribute(
                order,
                "created_at",
            )
        ),
    }


def get_my_orders(
    db: Session,
    current_user: User,
    limit: int = 5,
) -> dict:
    """
    Return ONLY orders belonging to
    the authenticated current user.

    There is intentionally no user_id
    argument.
    """

    limit = max(
        1,
        min(
            limit,
            10,
        ),
    )

    statement = (
        select(Order)
        .where(
            Order.user_id
            == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .limit(limit)
    )

    orders = list(
        db.scalars(
            statement
        ).all()
    )

    return {
        "count": len(orders),

        "orders": [
            build_order_tool_data(
                order
            )
            for order in orders
        ],
    }


def get_my_latest_order(
    db: Session,
    current_user: User,
) -> dict:
    """
    Return the authenticated user's
    newest order.
    """

    order = db.scalar(
        select(Order)
        .where(
            Order.user_id
            == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .limit(1)
    )

    if order is None:

        return {
            "found": False,
            "message": (
                "No orders were found "
                "for your account."
            ),
        }

    return {
        "found": True,
        "order": (
            build_order_tool_data(
                order
            )
        ),
    }


def get_my_order_status(
    db: Session,
    current_user: User,
    order_id: int,
) -> dict:
    """
    Return an order only when it belongs
    to current_user.

    A foreign order and a nonexistent
    order intentionally return the same
    response to avoid information leakage.
    """

    order = db.scalar(
        select(Order)
        .where(
            Order.id == order_id,
            Order.user_id
            == current_user.id,
        )
    )

    if order is None:

        return {
            "found": False,
            "message": (
                "Order not found "
                "in your account."
            ),
        }

    return {
        "found": True,
        "order": (
            build_order_tool_data(
                order
            )
        ),
    }