from decimal import Decimal

from pydantic import BaseModel

from app.schemas.order import OrderSummaryResponse


class DashboardResponse(BaseModel):
    customers: int
    products: int
    orders: int
    pending_orders: int
    low_stock: int
    todays_orders: int
    sales_total: Decimal

    recent_orders: list[
        OrderSummaryResponse
    ]