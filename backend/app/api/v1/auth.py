from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    MessageResponse,
    PasswordChange,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import (
    change_user_password,
    login_user,
    logout_user,
    refresh_user_tokens,
    register_user,
    update_user_profile,
)


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(
        db=db,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = login_user(
        db=db,
        login_data=login_data,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_tokens(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = refresh_user_tokens(
        db=db,
        token_data=token_data,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    logout_user(
        db=db,
        token_data=token_data,
    )

    return MessageResponse(
        message="Logged out successfully."
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return update_user_profile(
        db=db,
        user=current_user,
        user_data=user_data,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    change_user_password(
        db=db,
        user=current_user,
        password_data=password_data,
    )

    return MessageResponse(
        message="Password changed successfully."
    )