from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin_inventory import (
    AdminInventoryListResponse,
)
from app.services.admin_inventory_service import (
    list_admin_inventory,
)


router = APIRouter()


@router.get(
    "",
    response_model=AdminInventoryListResponse,
)
def get_admin_inventory(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    search: str | None = None,
    product_id: int | None = Query(
        default=None,
        gt=0,
    ),
    is_active: bool | None = None,
    low_stock: bool | None = None,
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    items, total = list_admin_inventory(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        product_id=product_id,
        is_active=is_active,
        low_stock=low_stock,
    )

    return AdminInventoryListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )