from decimal import Decimal

from pydantic import BaseModel


class AdminInventoryItemResponse(BaseModel):
    variant_id: int
    product_id: int

    product_name: str
    variant_name: str
    sku: str

    price_override: Decimal | None
    is_active: bool

    quantity: int
    low_stock_threshold: int
    is_low_stock: bool


class AdminInventoryListResponse(BaseModel):
    items: list[AdminInventoryItemResponse]

    page: int
    page_size: int
    total: int