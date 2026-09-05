from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    __table_args__ = (
        CheckConstraint(
            "quantity_change <> 0",
            name="ck_inventory_movement_non_zero",
        ),
        CheckConstraint(
            "balance_after >= 0",
            name="ck_inventory_movement_balance_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey(
            "product_variants.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )

    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )

    quantity_change: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    balance_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    variant = relationship(
        "ProductVariant",
        back_populates="movements",
    )