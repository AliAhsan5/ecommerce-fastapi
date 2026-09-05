from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import (
    create_product,
    get_product,
    list_products,
    update_product,
)


router = APIRouter()


@router.get(
    "",
    response_model=ProductListResponse,
)
def get_products(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
    ),
    brand_id: int | None = Query(
        default=None,
        ge=1,
    ),
    min_price: Decimal | None = Query(
        default=None,
        gt=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        gt=0,
    ),
    sort_by: Literal[
        "newest",
        "price_asc",
        "price_desc",
        "name_asc",
        "name_desc",
    ] = "newest",
    db: Session = Depends(get_db),
):
    products, total = list_products(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
    )

    return ProductListResponse(
        items=products,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product(
        db=db,
        product_id=product_id,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_product(
    product_data: ProductCreate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return create_product(
        db=db,
        product_data=product_data,
    )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_product(
        db=db,
        product_id=product_id,
        product_data=product_data,
    )