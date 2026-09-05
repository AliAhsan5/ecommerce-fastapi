from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product


def list_all_categories(
    db: Session,
    page: int,
    page_size: int,
) -> tuple[list[Category], int]:

    total = db.scalar(
        select(
            func.count(Category.id)
        )
    ) or 0

    categories = list(
        db.scalars(
            select(Category)
            .order_by(
                Category.name.asc()
            )
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
        ).all()
    )

    return categories, total


def list_all_brands(
    db: Session,
    page: int,
    page_size: int,
) -> tuple[list[Brand], int]:

    total = db.scalar(
        select(
            func.count(Brand.id)
        )
    ) or 0

    brands = list(
        db.scalars(
            select(Brand)
            .order_by(
                Brand.name.asc()
            )
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
        ).all()
    )

    return brands, total


def list_all_products(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    is_active: bool | None = None,
) -> tuple[list[Product], int]:

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
                Product.sku.ilike(
                    search_value
                ),
            )
        )


    if category_id is not None:
        conditions.append(
            Product.category_id
            == category_id
        )


    if brand_id is not None:
        conditions.append(
            Product.brand_id
            == brand_id
        )


    if is_active is not None:
        conditions.append(
            Product.is_active
            == is_active
        )


    total = db.scalar(
        select(
            func.count(Product.id)
        ).where(
            *conditions
        )
    ) or 0


    products = list(
        db.scalars(
            select(Product)
            .where(
                *conditions
            )
            .order_by(
                Product.created_at.desc()
            )
            .offset(
                (page - 1)
                * page_size
            )
            .limit(page_size)
        ).all()
    )


    return products, total