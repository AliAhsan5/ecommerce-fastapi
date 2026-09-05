from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    category_id: int = Field(gt=0)
    brand_id: int = Field(gt=0)

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    slug: str = Field(
        min_length=2,
        max_length=180,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    sku: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    sale_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class ProductUpdate(BaseModel):
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    brand_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=180,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    sale_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )

    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    category_id: int
    brand_id: int
    name: str
    slug: str
    sku: str
    description: str | None
    price: Decimal
    sale_price: Decimal | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total: int