from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)


def create_category(
    db: Session,
    category_data: CategoryCreate,
) -> Category:
    category = Category(
        name=category_data.name.strip(),
        slug=category_data.slug.lower(),
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Category name or slug already exists.",
            status_code=409,
        )

    return category


def list_categories(
    db: Session,
    page: int,
    page_size: int,
    active_only: bool = True,
) -> tuple[list[Category], int]:
    statement = select(Category)
    count_statement = select(
        func.count(Category.id)
    )

    if active_only:
        statement = statement.where(
            Category.is_active.is_(True)
        )
        count_statement = count_statement.where(
            Category.is_active.is_(True)
        )

    total = db.scalar(
        count_statement
    ) or 0

    categories = list(
        db.scalars(
            statement
            .order_by(Category.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    return categories, total


def get_category(
    db: Session,
    category_id: int,
    active_only: bool = True,
) -> Category:
    statement = select(Category).where(
        Category.id == category_id
    )

    if active_only:
        statement = statement.where(
            Category.is_active.is_(True)
        )

    category = db.scalar(statement)

    if category is None:
        raise AppException(
            message="Category not found.",
            status_code=404,
        )

    return category


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
) -> Category:
    category = get_category(
        db=db,
        category_id=category_id,
        active_only=False,
    )

    update_data = category_data.model_dump(
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
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="Category name or slug already exists.",
            status_code=409,
        )

    return category