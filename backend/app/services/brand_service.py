from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.brand import Brand
from app.schemas.brand import (
    BrandCreate,
    BrandUpdate,
)


def create_brand(
    db: Session,
    brand_data: BrandCreate,
) -> Brand:
    brand = Brand(
        name=brand_data.name.strip(),
        slug=brand_data.slug.lower(),
    )

    try:
        db.add(brand)
        db.commit()
        db.refresh(brand)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Brand name or slug already exists.",
            status_code=409,
        )

    return brand


def list_brands(
    db: Session,
    page: int,
    page_size: int,
    active_only: bool = True,
) -> tuple[list[Brand], int]:
    statement = select(Brand)

    count_statement = select(
        func.count(Brand.id)
    )

    if active_only:
        statement = statement.where(
            Brand.is_active.is_(True)
        )

        count_statement = count_statement.where(
            Brand.is_active.is_(True)
        )

    total = db.scalar(
        count_statement
    ) or 0

    brands = list(
        db.scalars(
            statement
            .order_by(Brand.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    return brands, total


def get_brand(
    db: Session,
    brand_id: int,
    active_only: bool = True,
) -> Brand:
    statement = select(Brand).where(
        Brand.id == brand_id
    )

    if active_only:
        statement = statement.where(
            Brand.is_active.is_(True)
        )

    brand = db.scalar(statement)

    if brand is None:
        raise AppException(
            message="Brand not found.",
            status_code=404,
        )

    return brand


def update_brand(
    db: Session,
    brand_id: int,
    brand_data: BrandUpdate,
) -> Brand:
    brand = get_brand(
        db=db,
        brand_id=brand_id,
        active_only=False,
    )

    update_data = brand_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        update_data["name"] = update_data[
            "name"
        ].strip()

    if "slug" in update_data:
        update_data["slug"] = update_data[
            "slug"
        ].lower()

    for field, value in update_data.items():
        setattr(
            brand,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(brand)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Brand name or slug already exists.",
            status_code=409,
        )

    return brand