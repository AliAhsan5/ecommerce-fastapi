from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import (
    BrandCreate,
    BrandListResponse,
    BrandResponse,
    BrandUpdate,
)
from app.services.brand_service import (
    create_brand,
    get_brand,
    list_brands,
    update_brand,
)


router = APIRouter()


@router.get(
    "",
    response_model=BrandListResponse,
)
def get_brands(
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
    brands, total = list_brands(
        db=db,
        page=page,
        page_size=page_size,
    )

    return BrandListResponse(
        items=brands,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
)
def get_brand_detail(
    brand_id: int,
    db: Session = Depends(get_db),
):
    return get_brand(
        db=db,
        brand_id=brand_id,
    )


@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_brand(
    brand_data: BrandCreate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return create_brand(
        db=db,
        brand_data=brand_data,
    )


@router.patch(
    "/{brand_id}",
    response_model=BrandResponse,
)
def update_existing_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_brand(
        db=db,
        brand_id=brand_id,
        brand_data=brand_data,
    )