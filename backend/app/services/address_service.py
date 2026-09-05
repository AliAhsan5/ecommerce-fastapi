from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.address import Address
from app.models.user import User
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
)


def get_owned_address(
    db: Session,
    user: User,
    address_id: int,
) -> Address:
    address = db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == user.id,
        )
    )

    if address is None:
        raise AppException(
            message="Address not found.",
            status_code=404,
        )

    return address


def clear_default_addresses(
    db: Session,
    user_id: int,
) -> None:
    db.execute(
        update(Address)
        .where(Address.user_id == user_id)
        .values(is_default=False)
    )


def create_address(
    db: Session,
    user: User,
    address_data: AddressCreate,
) -> Address:
    first_address = db.scalar(
        select(Address.id)
        .where(Address.user_id == user.id)
        .limit(1)
    )

    should_be_default = (
        first_address is None
        or address_data.is_default
    )

    if should_be_default:
        clear_default_addresses(
            db=db,
            user_id=user.id,
        )

    address = Address(
        user_id=user.id,
        **address_data.model_dump(
            exclude={"is_default"}
        ),
        is_default=should_be_default,
    )

    try:
        db.add(address)
        db.commit()
        db.refresh(address)

    except Exception:
        db.rollback()
        raise

    return address


def list_addresses(
    db: Session,
    user: User,
) -> list[Address]:
    return list(
        db.scalars(
            select(Address)
            .where(Address.user_id == user.id)
            .order_by(
                Address.is_default.desc(),
                Address.id.desc(),
            )
        ).all()
    )


def update_address(
    db: Session,
    user: User,
    address_id: int,
    address_data: AddressUpdate,
) -> Address:
    address = get_owned_address(
        db=db,
        user=user,
        address_id=address_id,
    )

    update_data = address_data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if update_data.get("is_default") is True:
        clear_default_addresses(
            db=db,
            user_id=user.id,
        )

    for field, value in update_data.items():
        setattr(
            address,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(address)

    except Exception:
        db.rollback()
        raise

    return address


def delete_address(
    db: Session,
    user: User,
    address_id: int,
) -> None:
    address = get_owned_address(
        db=db,
        user=user,
        address_id=address_id,
    )

    was_default = address.is_default

    try:
        db.delete(address)
        db.flush()

        if was_default:
            next_address = db.scalar(
                select(Address)
                .where(Address.user_id == user.id)
                .limit(1)
            )

            if next_address is not None:
                next_address.is_default = True

        db.commit()

    except Exception:
        db.rollback()
        raise