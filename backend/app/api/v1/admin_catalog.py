from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import BrandListResponse
from app.schemas.category import CategoryListResponse
from app.schemas.product import ProductListResponse
from app.services.admin_catalog_service import (
    list_all_brands,
    list_all_categories,
    list_all_products,
)


router = APIRouter()


@router.get(
    "/categories",
    response_model=CategoryListResponse,
)
def get_admin_categories(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    categories, total = (
        list_all_categories(
            db=db,
            page=page,
            page_size=page_size,
        )
    )

    return CategoryListResponse(
        items=categories,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/brands",
    response_model=BrandListResponse,
)
def get_admin_brands(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    brands, total = (
        list_all_brands(
            db=db,
            page=page,
            page_size=page_size,
        )
    )

    return BrandListResponse(
        items=brands,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/products",
    response_model=ProductListResponse,
)
def get_admin_products(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    brand_id: int | None = Query(
        default=None,
        gt=0,
    ),
    is_active: bool | None = None,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    products, total = (
        list_all_products(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            category_id=category_id,
            brand_id=brand_id,
            is_active=is_active,
        )
    )

    return ProductListResponse(
        items=products,
        page=page,
        page_size=page_size,
        total=total,
    )