from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import (
    create_category,
    get_category,
    list_categories,
    update_category,
)


router = APIRouter()


@router.get(
    "",
    response_model=CategoryListResponse,
)
def get_categories(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    categories, total = list_categories(
        db=db,
        page=page,
        page_size=page_size,
    )

    return CategoryListResponse(
        items=categories,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category_detail(
    category_id: int,
    db: Session = Depends(get_db),
):
    return get_category(
        db=db,
        category_id=category_id,
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=201,
)
def create_new_category(
    category_data: CategoryCreate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return create_category(
        db=db,
        category_data=category_data,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_category(
        db=db,
        category_id=category_id,
        category_data=category_data,
    )