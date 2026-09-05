from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.schemas.product_variant import (
    VariantCreate,
    VariantUpdate,
)


def create_variant(
    db: Session,
    variant_data: VariantCreate,
) -> ProductVariant:
    product = db.scalar(
        select(Product).where(
            Product.id == variant_data.product_id,
            Product.is_active.is_(True),
        )
    )

    if product is None:
        raise AppException(
            message="Active product not found.",
            status_code=404,
        )

    variant = ProductVariant(
        product_id=variant_data.product_id,
        name=variant_data.name.strip(),
        sku=variant_data.sku.upper(),
        price_override=variant_data.price_override,
    )

    try:
        db.add(variant)
        db.flush()

        inventory = Inventory(
            variant_id=variant.id,
            quantity=0,
            low_stock_threshold=(
                variant_data.low_stock_threshold
            ),
        )

        db.add(inventory)

        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Variant SKU already exists.",
            status_code=409,
        )

    except Exception:
        db.rollback()
        raise

    return variant


def list_variants(
    db: Session,
    product_id: int,
) -> list[ProductVariant]:
    return list(
        db.scalars(
            select(ProductVariant).where(
                ProductVariant.product_id == product_id,
                ProductVariant.is_active.is_(True),
            )
            .order_by(ProductVariant.id)
        ).all()
    )


def get_variant(
    db: Session,
    variant_id: int,
    active_only: bool = True,
) -> ProductVariant:
    statement = select(
        ProductVariant
    ).where(
        ProductVariant.id == variant_id
    )

    if active_only:
        statement = statement.where(
            ProductVariant.is_active.is_(True)
        )

    variant = db.scalar(statement)

    if variant is None:
        raise AppException(
            message="Product variant not found.",
            status_code=404,
        )

    return variant


def update_variant(
    db: Session,
    variant_id: int,
    variant_data: VariantUpdate,
) -> ProductVariant:
    variant = get_variant(
        db=db,
        variant_id=variant_id,
        active_only=False,
    )

    update_data = variant_data.model_dump(
        exclude_unset=True
    )

    if (
        "name" in update_data
        and update_data["name"] is not None
    ):
        update_data["name"] = update_data[
            "name"
        ].strip()

    if (
        "sku" in update_data
        and update_data["sku"] is not None
    ):
        update_data["sku"] = update_data[
            "sku"
        ].upper()

    for field, value in update_data.items():
        setattr(
            variant,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Variant SKU already exists.",
            status_code=409,
        )

    return variant