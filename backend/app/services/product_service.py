from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)


def validate_category(
    db: Session,
    category_id: int,
) -> None:
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
            Category.is_active.is_(True),
        )
    )

    if category is None:
        raise AppException(
            message="Active category not found.",
            status_code=404,
        )


def validate_brand(
    db: Session,
    brand_id: int,
) -> None:
    brand = db.scalar(
        select(Brand).where(
            Brand.id == brand_id,
            Brand.is_active.is_(True),
        )
    )

    if brand is None:
        raise AppException(
            message="Active brand not found.",
            status_code=404,
        )


def validate_prices(
    price: Decimal,
    sale_price: Decimal | None,
) -> None:
    if sale_price is not None and sale_price > price:
        raise AppException(
            message="Sale price cannot be greater than regular price.",
            status_code=400,
        )


def create_product(
    db: Session,
    product_data: ProductCreate,
) -> Product:
    validate_category(
        db=db,
        category_id=product_data.category_id,
    )

    validate_brand(
        db=db,
        brand_id=product_data.brand_id,
    )

    validate_prices(
        price=product_data.price,
        sale_price=product_data.sale_price,
    )

    product = Product(
        category_id=product_data.category_id,
        brand_id=product_data.brand_id,
        name=product_data.name.strip(),
        slug=product_data.slug.lower(),
        sku=product_data.sku.upper(),
        description=product_data.description,
        price=product_data.price,
        sale_price=product_data.sale_price,
        image_url=product_data.image_url,
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Product slug or SKU already exists.",
            status_code=409,
        )

    return product


def list_products(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort_by: str = "newest",
) -> tuple[list[Product], int]:
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise AppException(
            message="Minimum price cannot be greater than maximum price.",
            status_code=400,
        )

    filters = [
        Product.is_active.is_(True)
    ]

    if search:
        search_pattern = f"%{search.strip()}%"

        filters.append(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
                Product.description.ilike(
                    search_pattern
                ),
            )
        )

    if category_id is not None:
        filters.append(
            Product.category_id == category_id
        )

    if brand_id is not None:
        filters.append(
            Product.brand_id == brand_id
        )

    if min_price is not None:
        filters.append(
            Product.price >= min_price
        )

    if max_price is not None:
        filters.append(
            Product.price <= max_price
        )

    statement = select(Product).where(
        *filters
    )

    count_statement = select(
        func.count(Product.id)
    ).where(
        *filters
    )

    if sort_by == "price_asc":
        statement = statement.order_by(
            Product.price.asc()
        )

    elif sort_by == "price_desc":
        statement = statement.order_by(
            Product.price.desc()
        )

    elif sort_by == "name_asc":
        statement = statement.order_by(
            Product.name.asc()
        )

    elif sort_by == "name_desc":
        statement = statement.order_by(
            Product.name.desc()
        )

    else:
        statement = statement.order_by(
            Product.created_at.desc()
        )

    total = db.scalar(
        count_statement
    ) or 0

    products = list(
        db.scalars(
            statement
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
        ).all()
    )

    return products, total


def get_product(
    db: Session,
    product_id: int,
    active_only: bool = True,
) -> Product:
    statement = select(Product).where(
        Product.id == product_id
    )

    if active_only:
        statement = statement.where(
            Product.is_active.is_(True)
        )

    product = db.scalar(statement)

    if product is None:
        raise AppException(
            message="Product not found.",
            status_code=404,
        )

    return product


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate,
) -> Product:
    product = get_product(
        db=db,
        product_id=product_id,
        active_only=False,
    )

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    required_fields = {
        "category_id",
        "brand_id",
        "name",
        "slug",
        "sku",
        "price",
        "is_active",
    }

    for field in required_fields:
        if (
            field in update_data
            and update_data[field] is None
        ):
            raise AppException(
                message=f"{field} cannot be null.",
                status_code=400,
            )

    if "category_id" in update_data:
        validate_category(
            db=db,
            category_id=update_data[
                "category_id"
            ],
        )

    if "brand_id" in update_data:
        validate_brand(
            db=db,
            brand_id=update_data[
                "brand_id"
            ],
        )

    final_price = update_data.get(
        "price",
        product.price,
    )

    final_sale_price = update_data.get(
        "sale_price",
        product.sale_price,
    )

    validate_prices(
        price=final_price,
        sale_price=final_sale_price,
    )

    if "name" in update_data:
        update_data["name"] = update_data[
            "name"
        ].strip()

    if "slug" in update_data:
        update_data["slug"] = update_data[
            "slug"
        ].lower()

    if "sku" in update_data:
        update_data["sku"] = update_data[
            "sku"
        ].upper()

    for field, value in update_data.items():
        setattr(
            product,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Product slug or SKU already exists.",
            status_code=409,
        )

    return product