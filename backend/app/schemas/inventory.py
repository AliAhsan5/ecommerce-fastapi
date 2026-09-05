from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    low_stock_threshold: int
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class StockAdjustment(BaseModel):
    quantity_change: int

    reason: str = Field(
        min_length=3,
        max_length=255,
    )


class ThresholdUpdate(BaseModel):
    low_stock_threshold: int = Field(
        ge=0
    )


class InventoryMovementResponse(BaseModel):
    id: int
    variant_id: int
    created_by_user_id: int
    quantity_change: int
    balance_after: int
    reason: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class MovementListResponse(BaseModel):
    items: list[InventoryMovementResponse]
    page: int
    page_size: int
    total: int