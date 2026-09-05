from uuid import uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.category import Category


def test_commit():
    db = SessionLocal()

    try:
        existing_category = db.scalar(
            select(Category).where(Category.slug == "electronics")
        )

        if existing_category:
            print(
                f"Category already exists: "
                f"{existing_category.id} - {existing_category.name}"
            )
            return

        category = Category(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        print(
            f"Commit successful: "
            f"{category.id} - {category.name}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def test_read():
    db = SessionLocal()

    try:
        categories = db.scalars(
            select(Category)
        ).all()

        print("Categories in database:")

        for category in categories:
            print(
                category.id,
                category.name,
                category.slug,
                category.is_active,
            )

    finally:
        db.close()


def test_rollback():
    db = SessionLocal()

    test_id = uuid4().hex[:8]
    test_slug = f"rollback-test-{test_id}"

    try:
        category = Category(
            name=f"Rollback Test {test_id}",
            slug=test_slug,
            is_active=True,
        )

        db.add(category)

        db.flush()

        print(
            f"Temporary category created with ID: {category.id}"
        )

        db.rollback()

        saved_category = db.scalar(
            select(Category).where(
                Category.slug == test_slug
            )
        )

        if saved_category is None:
            print("Rollback successful: category was not saved.")
        else:
            print("Rollback failed: category still exists.")

    finally:
        db.close()


if __name__ == "__main__":
    test_commit()
    test_read()
    test_rollback()