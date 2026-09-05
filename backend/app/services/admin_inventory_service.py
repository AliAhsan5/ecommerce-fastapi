from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_variant import ProductVariant


def list_admin_inventory(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    product_id: int | None = None,
    is_active: bool | None = None,
    low_stock: bool | None = None,
) -> tuple[list[dict], int]:

    conditions = []


    if search:
        search_value = (
            f"%{search.strip()}%"
        )

        conditions.append(
            or_(
                Product.name.ilike(
                    search_value
                ),
                ProductVariant.name.ilike(
                    search_value
                ),
                ProductVariant.sku.ilike(
                    search_value
                ),
            )
        )


    if product_id is not None:
        conditions.append(
            ProductVariant.product_id
            == product_id
        )


    if is_active is not None:
        conditions.append(
            ProductVariant.is_active
            == is_active
        )


    if low_stock is True:
        conditions.append(
            Inventory.quantity
            <= Inventory.low_stock_threshold
        )


    if low_stock is False:
        conditions.append(
            Inventory.quantity
            > Inventory.low_stock_threshold
        )


    total = db.scalar(
        select(
            func.count(
                ProductVariant.id
            )
        )
        .select_from(
            ProductVariant
        )
        .join(
            Product,
            Product.id
            == ProductVariant.product_id,
        )
        .join(
            Inventory,
            Inventory.variant_id
            == ProductVariant.id,
        )
        .where(
            *conditions
        )
    ) or 0


    rows = db.execute(
        select(
            ProductVariant,
            Product,
            Inventory,
        )
        .join(
            Product,
            Product.id
            == ProductVariant.product_id,
        )
        .join(
            Inventory,
            Inventory.variant_id
            == ProductVariant.id,
        )
        .where(
            *conditions
        )
        .order_by(
            Product.name.asc(),
            ProductVariant.name.asc(),
        )
        .offset(
            (page - 1) * page_size
        )
        .limit(
            page_size
        )
    ).all()


    items = []


    for variant, product, inventory in rows:

        items.append(
            {
                "variant_id":
                    variant.id,

                "product_id":
                    product.id,

                "product_name":
                    product.name,

                "variant_name":
                    variant.name,

                "sku":
                    variant.sku,

                "price_override":
                    variant.price_override,

                "is_active":
                    variant.is_active,

                "quantity":
                    inventory.quantity,

                "low_stock_threshold":
                    inventory.low_stock_threshold,

                "is_low_stock":
                    inventory.quantity
                    <= inventory.low_stock_threshold,
            }
        )


    return items, total