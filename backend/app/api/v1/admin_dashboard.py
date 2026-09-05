from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
)
from app.services.dashboard_service import (
    get_dashboard_metrics,
)


router = APIRouter()


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_admin_dashboard(
    current_admin: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db),
):
    return get_dashboard_metrics(
        db=db
    )