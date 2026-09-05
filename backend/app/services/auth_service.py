from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    RefreshTokenRequest,
    UserCreate,
    UserLogin,
    UserUpdate,
)


def register_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    email = str(user_data.email).lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise AppException(
            message="An account with this email already exists.",
            status_code=409,
        )

    user = User(
        full_name=user_data.full_name,
        email=email,
        password_hash=hash_password(user_data.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise AppException(
            message="An account with this email already exists.",
            status_code=409,
        )

    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    login_data: UserLogin,
) -> User:
    email = str(login_data.email).lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise AppException(
            message="Invalid email or password.",
            status_code=401,
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise AppException(
            message="Invalid email or password.",
            status_code=401,
        )

    if not user.is_active:
        raise AppException(
            message="This account is inactive.",
            status_code=403,
        )

    return user


def create_token_pair(
    db: Session,
    user: User,
) -> tuple[str, str]:
    access_token = create_access_token(
        subject=str(user.id)
    )

    raw_refresh_token = create_refresh_token()

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(
            raw_refresh_token
        ),
        expires_at=get_refresh_token_expiry(),
    )

    db.add(refresh_token_record)

    return access_token, raw_refresh_token


def login_user(
    db: Session,
    login_data: UserLogin,
) -> tuple[str, str]:
    user = authenticate_user(
        db=db,
        login_data=login_data,
    )

    try:
        access_token, refresh_token = create_token_pair(
            db=db,
            user=user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return access_token, refresh_token


def refresh_user_tokens(
    db: Session,
    token_data: RefreshTokenRequest,
) -> tuple[str, str]:
    token_hash = hash_refresh_token(
        token_data.refresh_token
    )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if stored_token is None:
        raise AppException(
            message="Invalid refresh token.",
            status_code=401,
        )

    if stored_token.revoked_at is not None:
        raise AppException(
            message="Invalid refresh token.",
            status_code=401,
        )

    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise AppException(
            message="Refresh token has expired.",
            status_code=401,
        )

    user = db.scalar(
        select(User).where(
            User.id == stored_token.user_id
        )
    )

    if user is None:
        raise AppException(
            message="Invalid refresh token.",
            status_code=401,
        )

    if not user.is_active:
        raise AppException(
            message="This account is inactive.",
            status_code=403,
        )

    try:
        stored_token.revoked_at = datetime.now(
            timezone.utc
        )

        access_token, refresh_token = create_token_pair(
            db=db,
            user=user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return access_token, refresh_token


def logout_user(
    db: Session,
    token_data: RefreshTokenRequest,
) -> None:
    token_hash = hash_refresh_token(
        token_data.refresh_token
    )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if stored_token is None:
        raise AppException(
            message="Invalid refresh token.",
            status_code=401,
        )

    if stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(
            timezone.utc
        )

        try:
            db.commit()

        except Exception:
            db.rollback()
            raise


def update_user_profile(
    db: Session,
    user: User,
    user_data: UserUpdate,
) -> User:
    user.full_name = user_data.full_name

    try:
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return user


def change_user_password(
    db: Session,
    user: User,
    password_data: PasswordChange,
) -> None:
    if not verify_password(
        password_data.current_password,
        user.password_hash,
    ):
        raise AppException(
            message="Current password is incorrect.",
            status_code=400,
        )

    if verify_password(
        password_data.new_password,
        user.password_hash,
    ):
        raise AppException(
            message="New password must be different from the current password.",
            status_code=400,
        )

    user.password_hash = hash_password(
        password_data.new_password
    )

    try:
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise