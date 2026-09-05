from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "variant_id",
            name="uq_cart_item_variant",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_cart_item_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    cart_id: Mapped[int] = mapped_column(
        ForeignKey(
            "carts.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey(
            "product_variants.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cart = relationship(
        "Cart",
        back_populates="items",
    )

    variant = relationship(
        "ProductVariant"
    )