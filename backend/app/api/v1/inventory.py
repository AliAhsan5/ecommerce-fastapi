from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryResponse,
    MovementListResponse,
    StockAdjustment,
    ThresholdUpdate,
)
from app.services.inventory_service import (
    adjust_inventory,
    get_inventory,
    list_movements,
    update_threshold,
)


router = APIRouter()


@router.get(
    "/{variant_id}",
    response_model=InventoryResponse,
)
def get_variant_inventory(
    variant_id: int,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return get_inventory(
        db=db,
        variant_id=variant_id,
    )


@router.post(
    "/{variant_id}/adjust",
    response_model=InventoryResponse,
)
def adjust_variant_inventory(
    variant_id: int,
    adjustment: StockAdjustment,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return adjust_inventory(
        db=db,
        variant_id=variant_id,
        adjustment=adjustment,
        admin=current_admin,
    )


@router.patch(
    "/{variant_id}/threshold",
    response_model=InventoryResponse,
)
def change_low_stock_threshold(
    variant_id: int,
    threshold_data: ThresholdUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_threshold(
        db=db,
        variant_id=variant_id,
        threshold_data=threshold_data,
    )


@router.get(
    "/{variant_id}/movements",
    response_model=MovementListResponse,
)
def get_inventory_movements(
    variant_id: int,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    movements, total = list_movements(
        db=db,
        variant_id=variant_id,
        page=page,
        page_size=page_size,
    )

    return MovementListResponse(
        items=movements,
        page=page,
        page_size=page_size,
        total=total,
    )