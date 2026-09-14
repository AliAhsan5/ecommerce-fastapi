from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.services.product_context_service import (
    get_effective_price,
)
from app.services.inventory_service import (
    get_inventory,
)
from app.services.product_service import (
    get_product,
    list_products,
)


def get_variant_stock(
    db: Session,
    variant_id: int,
) -> int:
    """
    Return current stock quantity
    for a product variant.

    If an inventory record does not
    exist, treat stock as zero.
    """

    try:
        inventory = get_inventory(
            db=db,
            variant_id=variant_id,
        )

        return inventory.quantity

    except AppException:
        return 0


def build_product_tool_data(
    db: Session,
    product,
) -> dict:
    """
    Convert a Product model into
    safe structured data for AI tools.
    """

    variants = []

    for variant in product.variants:

        if not variant.is_active:
            continue

        effective_price = (
            get_effective_price(
                product=product,
                variant=variant,
            )
        )

        stock_quantity = (
            get_variant_stock(
                db=db,
                variant_id=variant.id,
            )
        )

        variants.append(
            {
                "variant_id": variant.id,
                "name": variant.name,
                "sku": variant.sku,

                "effective_price": (
                    effective_price
                ),

                "stock_quantity": (
                    stock_quantity
                ),

                "availability": (
                    "in_stock"
                    if stock_quantity > 0
                    else "out_of_stock"
                ),
            }
        )

    return {
        "product_id": product.id,
        "name": product.name,
        "slug": product.slug,
        "sku": product.sku,

        "description": (
            product.description
        ),

        "base_price": (
            product.price
        ),

        "sale_price": (
            product.sale_price
        ),

        "category_id": (
            product.category_id
        ),

        "brand_id": (
            product.brand_id
        ),

        "image_url": (
            product.image_url
        ),

        "variants": variants,
    }


def search_products(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    limit: int = 5,
) -> dict:
    """
    Search active store products using
    the existing product service.
    """

    if limit < 1:
        limit = 1

    if limit > 10:
        limit = 10

    products, total = list_products(
        db=db,
        page=1,
        page_size=limit,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        sort_by="newest",
    )

    results = []

    for product in products:

        results.append(
            build_product_tool_data(
                db=db,
                product=product,
            )
        )

    return {
        "total": total,
        "returned": len(results),
        "products": results,
    }


def get_product_detail(
    db: Session,
    product_id: int,
) -> dict:
    """
    Return complete verified information
    for one active product.
    """

    product = get_product(
        db=db,
        product_id=product_id,
        active_only=True,
    )

    return build_product_tool_data(
        db=db,
        product=product,
    )


def check_stock(
    db: Session,
    variant_id: int,
) -> dict:
    """
    Check verified inventory for a
    specific variant.
    """

    inventory = get_inventory(
        db=db,
        variant_id=variant_id,
    )

    return {
        "variant_id": variant_id,

        "stock_quantity": (
            inventory.quantity
        ),

        "low_stock_threshold": (
            inventory.low_stock_threshold
        ),

        "availability": (
            "in_stock"
            if inventory.quantity > 0
            else "out_of_stock"
        ),

        "low_stock": (
            inventory.quantity
            <= inventory.low_stock_threshold
        ),
    }


def compare_products(
    db: Session,
    product_ids: list[int],
) -> dict:
    """
    Return verified structured data
    for exactly two products.

    Gemini can then explain the
    differences without inventing facts.
    """

    unique_ids = list(
        dict.fromkeys(
            product_ids
        )
    )

    if len(unique_ids) != 2:

        raise AppException(
            message=(
                "Exactly two different "
                "products are required "
                "for comparison."
            ),
            status_code=400,
        )

    products = []

    for product_id in unique_ids:

        product = get_product(
            db=db,
            product_id=product_id,
            active_only=True,
        )

        products.append(
            build_product_tool_data(
                db=db,
                product=product,
            )
        )

    return {
        "products": products,
        "comparison_count": 2,
    }