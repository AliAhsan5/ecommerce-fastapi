from fastapi import APIRouter, Depends

from app.api.deps import require_admin
from app.models.user import User


router = APIRouter()


@router.get("/test")
def admin_test(
    current_admin: User = Depends(
        require_admin
    ),
):
    return {
        "message": "Admin access granted.",
        "user_id": current_admin.id,
        "role": current_admin.role,
    }