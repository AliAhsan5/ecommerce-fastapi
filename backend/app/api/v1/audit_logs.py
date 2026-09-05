from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import (
    AuditLogListResponse,
)
from app.services.audit_service import (
    list_audit_logs,
)


router = APIRouter()


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def get_audit_logs(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    action: str | None = None,
    entity_type: str | None = None,
    user_id: int | None = Query(
        default=None,
        gt=0,
    ),
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    logs, total = list_audit_logs(
        db=db,
        page=page,
        page_size=page_size,
        action=action,
        entity_type=entity_type,
        user_id=user_id,
    )


    return AuditLogListResponse(
        items=logs,
        page=page,
        page_size=page_size,
        total=total,
    )