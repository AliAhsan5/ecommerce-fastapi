import re
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_variant import ProductVariant


STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "for",
    "of",
    "to",
    "in",
    "on",
    "is",
    "are",
    "do",
    "you",
    "your",
    "have",
    "has",
    "show",
    "tell",
    "find",
    "give",
    "need",
    "want",
    "looking",
    "please",
    "product",
    "products",
    "item",
    "items",
    "available",
    "availability",
    "stock",
    "price",
    "budget",
    "under",
    "below",
    "within",
    "upto",
    "up",
    "less",
    "than",
    "what",
    "which",
    "me",

    # Roman Urdu common words
    "mujhe",
    "mujhy",
    "koi",
    "batao",
    "bata",
    "dikhao",
    "dikha",
    "chahiye",
    "chaiye",
    "hai",
    "hain",
    "ka",
    "ki",
    "ke",
    "kay",
    "se",
    "say",
    "kam",
    "andar",
    "tak",
    "wala",
    "wali",
    "walay",

    "rs",
    "pkr",
}


def get_effective_price(
    product_price: Decimal,
    sale_price: Decimal | None,
    variant_price: Decimal | None,
) -> Decimal:

    if variant_price is not None:
        return variant_price

    if sale_price is not None:
        return sale_price

    return product_price


def extract_max_price(
    message: str,
) -> Decimal | None:

    normalized = (
        message.lower()
        .replace(",", "")
    )


    patterns = [
        r"(?:under|below|within|upto|up to|less than)\s*(?:rs\.?|pkr)?\s*(\d+(?:\.\d+)?)",

        r"(?:rs\.?|pkr)?\s*(\d+(?:\.\d+)?)\s*(?:ke andar|se kam|tak)",

        r"(?:budget(?: of)?|budget is)\s*(?:rs\.?|pkr)?\s*(\d+(?:\.\d+)?)",

        r"(?:rs\.?|pkr)?\s*(\d+(?:\.\d+)?)\s*budget",
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            normalized,
        )

        if match:
            return Decimal(
                match.group(1)
            )


    return None


def extract_search_terms(
    message: str,
) -> list[str]:

    words = re.findall(
        r"[a-zA-Z0-9]+",
        message.lower(),
    )


    terms = []


    for word in words:

        if word.isdigit():
            continue

        if word in STOP_WORDS:
            continue

        if len(word) < 2:
            continue

        if word not in terms:
            terms.append(word)


    return terms


def build_product_context(
    rows,
) -> tuple[str, list[dict]]:

    context_lines = []

    products = []


    for (
        product,
        variant,
        inventory,
        category,
        brand,
    ) in rows:

        effective_price = (
            get_effective_price(
                product_price=
                    product.price,

                sale_price=
                    product.sale_price,

                variant_price=
                    variant.price_override,
            )
        )


        context_lines.append(
            "\n".join(
                [
                    f"Product ID: {product.id}",

                    (
                        f"Product Name: "
                        f"{product.name}"
                    ),

                    (
                        f"Product Slug: "
                        f"{product.slug}"
                    ),

                    (
                        f"Category: "
                        f"{category.name}"
                    ),

                    (
                        f"Brand: "
                        f"{brand.name}"
                    ),

                    (
                        f"Variant ID: "
                        f"{variant.id}"
                    ),

                    (
                        f"Variant: "
                        f"{variant.name}"
                    ),

                    f"SKU: {variant.sku}",

                    (
                        f"Price: PKR "
                        f"{effective_price}"
                    ),

                    (
                        f"Stock Quantity: "
                        f"{inventory.quantity}"
                    ),

                    (
                        "Availability: In Stock"
                        if inventory.quantity > 0
                        else
                        "Availability: Out of Stock"
                    ),

                    "---",
                ]
            )
        )


        products.append(
            {
                "id":
                    product.id,

                "name":
                    product.name,

                "slug":
                    product.slug,

                "image_url":
                    product.image_url,

                "variant_id":
                    variant.id,

                "variant_name":
                    variant.name,

                "effective_price":
                    effective_price,

                "stock_quantity":
                    inventory.quantity,
            }
        )


    if not context_lines:

        return (
            (
                "No matching verified active "
                "store products were found."
            ),
            [],
        )


    return (
        "\n".join(
            context_lines
        ),
        products,
    )


def get_store_product_context(
    db: Session,
    limit: int = 50,
) -> tuple[str, list[dict]]:

    rows = db.execute(
        select(
            Product,
            ProductVariant,
            Inventory,
            Category,
            Brand,
        )
        .join(
            ProductVariant,
            ProductVariant.product_id
            == Product.id,
        )
        .join(
            Inventory,
            Inventory.variant_id
            == ProductVariant.id,
        )
        .join(
            Category,
            Category.id
            == Product.category_id,
        )
        .join(
            Brand,
            Brand.id
            == Product.brand_id,
        )
        .where(
            Product.is_active.is_(
                True
            ),

            ProductVariant.is_active.is_(
                True
            ),

            Category.is_active.is_(
                True
            ),

            Brand.is_active.is_(
                True
            ),
        )
        .order_by(
            Product.name.asc(),
            ProductVariant.name.asc(),
        )
        .limit(limit)
    ).all()


    return build_product_context(
        rows
    )


def get_relevant_product_context(
    db: Session,
    message: str,
    limit: int = 10,
) -> tuple[str, list[dict]]:

    max_price = extract_max_price(
        message
    )

    search_terms = extract_search_terms(
        message
    )


    effective_price_expression = (
        func.coalesce(
            ProductVariant.price_override,
            Product.sale_price,
            Product.price,
        )
    )


    query = (
        select(
            Product,
            ProductVariant,
            Inventory,
            Category,
            Brand,
        )
        .join(
            ProductVariant,
            ProductVariant.product_id
            == Product.id,
        )
        .join(
            Inventory,
            Inventory.variant_id
            == ProductVariant.id,
        )
        .join(
            Category,
            Category.id
            == Product.category_id,
        )
        .join(
            Brand,
            Brand.id
            == Product.brand_id,
        )
        .where(
            Product.is_active.is_(
                True
            ),

            ProductVariant.is_active.is_(
                True
            ),

            Category.is_active.is_(
                True
            ),

            Brand.is_active.is_(
                True
            ),
        )
    )


    if max_price is not None:

        query = query.where(
            effective_price_expression
            <= max_price
        )


    if search_terms:

        term_conditions = []


        for term in search_terms:

            pattern = f"%{term}%"


            term_conditions.append(
                or_(
                    Product.name.ilike(
                        pattern
                    ),

                    Product.description.ilike(
                        pattern
                    ),

                    Product.sku.ilike(
                        pattern
                    ),

                    Category.name.ilike(
                        pattern
                    ),

                    Brand.name.ilike(
                        pattern
                    ),

                    ProductVariant.name.ilike(
                        pattern
                    ),

                    ProductVariant.sku.ilike(
                        pattern
                    ),
                )
            )


        query = query.where(
                *term_conditions     
        )


    if max_price is not None:

        query = query.order_by(
            effective_price_expression.asc(),
            Product.name.asc(),
        )

    else:

        query = query.order_by(
            Product.name.asc(),
            ProductVariant.name.asc(),
        )


    rows = db.execute(
        query.limit(limit)
    ).all()


    return build_product_context(
        rows
    )