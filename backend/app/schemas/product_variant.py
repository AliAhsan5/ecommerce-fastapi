from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class VariantCreate(BaseModel):
    product_id: int = Field(gt=0)

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    sku: str = Field(
        min_length=2,
        max_length=100,
    )

    price_override: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    low_stock_threshold: int = Field(
        default=5,
        ge=0,
    )


class VariantUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    price_override: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    is_active: bool | None = None


class VariantResponse(BaseModel):
    id: int
    product_id: int
    name: str
    sku: str
    price_override: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )