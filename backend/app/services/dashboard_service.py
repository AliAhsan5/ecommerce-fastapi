from datetime import (
    datetime,
    time,
    timedelta,
    timezone,
)
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User


def get_dashboard_metrics(
    db: Session,
) -> dict:

    now_utc = datetime.now(
        timezone.utc
    )

    today_start = datetime.combine(
        now_utc.date(),
        time.min,
        tzinfo=timezone.utc,
    )

    tomorrow_start = (
        today_start
        + timedelta(days=1)
    )


    customers = db.scalar(
        select(
            func.count(User.id)
        ).where(
            User.role == "customer"
        )
    ) or 0


    products = db.scalar(
        select(
            func.count(Product.id)
        )
    ) or 0


    orders = db.scalar(
        select(
            func.count(Order.id)
        )
    ) or 0


    pending_orders = db.scalar(
        select(
            func.count(Order.id)
        ).where(
            Order.status == "pending"
        )
    ) or 0


    low_stock = db.scalar(
        select(
            func.count(Inventory.id)
        ).where(
            Inventory.quantity
            <= Inventory.low_stock_threshold
        )
    ) or 0


    todays_orders = db.scalar(
        select(
            func.count(Order.id)
        ).where(
            Order.created_at
            >= today_start,
            Order.created_at
            < tomorrow_start,
        )
    ) or 0


    sales_total = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    Order.total_amount
                ),
                0,
            )
        ).where(
            Order.status
            == "delivered"
        )
    )


    if sales_total is None:
        sales_total = Decimal("0.00")


    recent_orders = list(
        db.scalars(
            select(Order)
            .order_by(
                Order.created_at.desc()
            )
            .limit(5)
        ).all()
    )


    return {
        "customers":
            customers,

        "products":
            products,

        "orders":
            orders,

        "pending_orders":
            pending_orders,

        "low_stock":
            low_stock,

        "todays_orders":
            todays_orders,

        "sales_total":
            sales_total,

        "recent_orders":
            recent_orders,
    }