from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppException(
            message="Authentication required.",
            status_code=401,
        )

    payload = decode_access_token(
        credentials.credentials
    )

    subject = payload.get("sub")

    try:
        user_id = int(subject)

    except (TypeError, ValueError):
        raise AppException(
            message="Invalid access token.",
            status_code=401,
        )

    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise AppException(
            message="Invalid access token.",
            status_code=401,
        )

    if not user.is_active:
        raise AppException(
            message="This account is inactive.",
            status_code=403,
        )

    return user


def require_admin(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    if current_user.role != "admin":
        raise AppException(
            message="Administrator access required.",
            status_code=403,
        )

    return current_user