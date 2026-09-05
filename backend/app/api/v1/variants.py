from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.product_variant import (
    VariantCreate,
    VariantResponse,
    VariantUpdate,
)
from app.services.variant_service import (
    create_variant,
    get_variant,
    list_variants,
    update_variant,
)


router = APIRouter()


@router.get(
    "/product/{product_id}",
    response_model=list[VariantResponse],
)
def get_product_variants(
    product_id: int,
    db: Session = Depends(get_db),
):
    return list_variants(
        db=db,
        product_id=product_id,
    )


@router.get(
    "/{variant_id}",
    response_model=VariantResponse,
)
def get_variant_detail(
    variant_id: int,
    db: Session = Depends(get_db),
):
    return get_variant(
        db=db,
        variant_id=variant_id,
    )


@router.post(
    "",
    response_model=VariantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_variant(
    variant_data: VariantCreate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return create_variant(
        db=db,
        variant_data=variant_data,
    )


@router.patch(
    "/{variant_id}",
    response_model=VariantResponse,
)
def update_existing_variant(
    variant_id: int,
    variant_data: VariantUpdate,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return update_variant(
        db=db,
        variant_id=variant_id,
        variant_data=variant_data,
    )