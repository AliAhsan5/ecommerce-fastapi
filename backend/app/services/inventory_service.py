from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.inventory import (
    StockAdjustment,
    ThresholdUpdate,
)


def get_inventory(
    db: Session,
    variant_id: int,
) -> Inventory:
    inventory = db.scalar(
        select(Inventory).where(
            Inventory.variant_id == variant_id
        )
    )

    if inventory is None:
        raise AppException(
            message="Inventory not found.",
            status_code=404,
        )

    return inventory


def adjust_inventory(
    db: Session,
    variant_id: int,
    adjustment: StockAdjustment,
    admin: User,
) -> Inventory:

    if adjustment.quantity_change == 0:
        raise AppException(
            message="Quantity change cannot be zero.",
            status_code=400,
        )

    inventory = db.scalar(
        select(Inventory)
        .where(
            Inventory.variant_id == variant_id
        )
        .with_for_update()
    )

    if inventory is None:
        raise AppException(
            message="Inventory not found.",
            status_code=404,
        )

    new_quantity = (
        inventory.quantity
        + adjustment.quantity_change
    )

    if new_quantity < 0:
        raise AppException(
            message="Stock cannot become negative.",
            status_code=400,
        )

    inventory.quantity = new_quantity


    movement = InventoryMovement(
        variant_id=variant_id,
        created_by_user_id=admin.id,
        quantity_change=(
            adjustment.quantity_change
        ),
        balance_after=new_quantity,
        reason=adjustment.reason.strip(),
    )


    audit_log = AuditLog(
        user_id=admin.id,
        action="inventory_adjusted",
        entity_type="product_variant",
        entity_id=variant_id,
        details=(
            f"Quantity change: "
            f"{adjustment.quantity_change}; "
            f"Balance after: "
            f"{new_quantity}; "
            f"Reason: "
            f"{adjustment.reason.strip()}"
        ),
    )


    try:
        db.add(movement)
        db.add(audit_log)

        db.commit()

        db.refresh(inventory)

    except Exception:
        db.rollback()
        raise


    return inventory


def update_threshold(
    db: Session,
    variant_id: int,
    threshold_data: ThresholdUpdate,
) -> Inventory:
    inventory = get_inventory(
        db=db,
        variant_id=variant_id,
    )

    inventory.low_stock_threshold = (
        threshold_data.low_stock_threshold
    )

    try:
        db.commit()
        db.refresh(inventory)

    except Exception:
        db.rollback()
        raise

    return inventory


def list_movements(
    db: Session,
    variant_id: int,
    page: int,
    page_size: int,
) -> tuple[list[InventoryMovement], int]:
    total = db.scalar(
        select(
            func.count(
                InventoryMovement.id
            )
        ).where(
            InventoryMovement.variant_id
            == variant_id
        )
    ) or 0

    movements = list(
        db.scalars(
            select(InventoryMovement)
            .where(
                InventoryMovement.variant_id
                == variant_id
            )
            .order_by(
                InventoryMovement.created_at.desc()
            )
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
        ).all()
    )

    return movements, total