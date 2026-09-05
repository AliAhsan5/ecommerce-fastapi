from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CheckoutRequest(BaseModel):
    address_id: int = Field(gt=0)

    idempotency_key: str = Field(
        min_length=8,
        max_length=100,
    )

    payment_method: Literal["cod"] = "cod"


class OrderItemResponse(BaseModel):
    id: int
    variant_id: int | None
    product_name: str
    variant_name: str
    sku: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderStatusHistoryResponse(BaseModel):
    id: int
    status: str
    changed_by_user_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderSummaryResponse(BaseModel):
    id: int
    subtotal: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    payment_method: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderListResponse(BaseModel):
    items: list[OrderSummaryResponse]
    page: int
    page_size: int
    total: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    shipping_address_id: int | None

    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str | None
    country: str

    subtotal: Decimal
    shipping_amount: Decimal
    total_amount: Decimal

    payment_method: str
    status: str

    created_at: datetime
    updated_at: datetime

    items: list[OrderItemResponse]
    status_history: list[
        OrderStatusHistoryResponse
    ]

    model_config = ConfigDict(
        from_attributes=True
    )