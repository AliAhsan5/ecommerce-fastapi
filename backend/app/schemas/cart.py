from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    variant_id: int = Field(
        gt=0
    )

    quantity: int = Field(
        ge=1
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        ge=1
    )


class CartItemResponse(BaseModel):
    id: int
    variant_id: int
    product_id: int

    product_name: str
    variant_name: str
    sku: str

    quantity: int

    unit_price: Decimal
    subtotal: Decimal


class CartResponse(BaseModel):
    id: int
    user_id: int

    items: list[CartItemResponse]

    total_items: int
    subtotal: Decimal