from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from app.core.exceptions import AppException
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.schemas.cart import (
    CartItemAdd,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
)


def get_or_create_cart(
    db: Session,
    user: User,
) -> Cart:
    cart = db.scalar(
        select(Cart).where(
            Cart.user_id == user.id
        )
    )

    if cart is not None:
        return cart

    cart = Cart(
        user_id=user.id
    )

    try:
        db.add(cart)
        db.commit()
        db.refresh(cart)

    except Exception:
        db.rollback()
        raise

    return cart


def get_sellable_variant(
    db: Session,
    variant_id: int,
) -> ProductVariant:
    variant = db.scalar(
        select(ProductVariant)
        .options(
            joinedload(
                ProductVariant.product
            ),
            joinedload(
                ProductVariant.inventory
            ),
        )
        .where(
            ProductVariant.id == variant_id
        )
    )

    if variant is None:
        raise AppException(
            message="Product variant not found.",
            status_code=404,
        )

    if not variant.is_active:
        raise AppException(
            message="Product variant is inactive.",
            status_code=400,
        )

    if not variant.product.is_active:
        raise AppException(
            message="Product is inactive.",
            status_code=400,
        )

    if variant.inventory is None:
        raise AppException(
            message="Inventory not found.",
            status_code=400,
        )

    return variant


def get_effective_price(
    variant: ProductVariant,
) -> Decimal:
    if variant.price_override is not None:
        return variant.price_override

    product = variant.product

    if product.sale_price is not None:
        return product.sale_price

    return product.price


def build_cart_response(
    db: Session,
    cart_id: int,
) -> CartResponse:
    cart = db.scalar(
        select(Cart)
        .options(
            selectinload(Cart.items)
            .joinedload(CartItem.variant)
            .joinedload(
                ProductVariant.product
            )
        )
        .where(
            Cart.id == cart_id
        )
    )

    if cart is None:
        raise AppException(
            message="Cart not found.",
            status_code=404,
        )

    response_items = []

    total_items = 0

    cart_subtotal = Decimal(
        "0.00"
    )

    for item in cart.items:
        variant = item.variant

        unit_price = get_effective_price(
            variant
        )

        item_subtotal = (
            unit_price * item.quantity
        )

        total_items += item.quantity

        cart_subtotal += item_subtotal

        response_items.append(
            CartItemResponse(
                id=item.id,
                variant_id=variant.id,
                product_id=(
                    variant.product.id
                ),
                product_name=(
                    variant.product.name
                ),
                variant_name=(
                    variant.name
                ),
                sku=variant.sku,
                quantity=item.quantity,
                unit_price=unit_price,
                subtotal=item_subtotal,
            )
        )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=response_items,
        total_items=total_items,
        subtotal=cart_subtotal,
    )


def get_user_cart(
    db: Session,
    user: User,
) -> CartResponse:
    cart = get_or_create_cart(
        db=db,
        user=user,
    )

    return build_cart_response(
        db=db,
        cart_id=cart.id,
    )


def add_cart_item(
    db: Session,
    user: User,
    item_data: CartItemAdd,
) -> CartResponse:
    variant = get_sellable_variant(
        db=db,
        variant_id=item_data.variant_id,
    )

    cart = get_or_create_cart(
        db=db,
        user=user,
    )

    existing_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.variant_id
            == variant.id,
        )
    )

    if existing_item is None:
        new_quantity = (
            item_data.quantity
        )

    else:
        new_quantity = (
            existing_item.quantity
            + item_data.quantity
        )

    if (
        new_quantity >
        variant.inventory.quantity
    ):
        raise AppException(
            message="Requested quantity exceeds available stock.",
            status_code=400,
        )

    try:
        if existing_item is None:
            cart_item = CartItem(
                cart_id=cart.id,
                variant_id=variant.id,
                quantity=new_quantity,
            )

            db.add(cart_item)

        else:
            existing_item.quantity = (
                new_quantity
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return build_cart_response(
        db=db,
        cart_id=cart.id,
    )


def update_cart_item(
    db: Session,
    user: User,
    item_id: int,
    item_data: CartItemUpdate,
) -> CartResponse:
    cart = get_or_create_cart(
        db=db,
        user=user,
    )

    item = db.scalar(
        select(CartItem)
        .options(
            joinedload(
                CartItem.variant
            )
            .joinedload(
                ProductVariant.product
            ),
            joinedload(
                CartItem.variant
            )
            .joinedload(
                ProductVariant.inventory
            ),
        )
        .where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    if item is None:
        raise AppException(
            message="Cart item not found.",
            status_code=404,
        )

    variant = item.variant

    if (
        not variant.is_active
        or not variant.product.is_active
    ):
        raise AppException(
            message="Product is no longer available.",
            status_code=400,
        )

    if (
        variant.inventory is None
        or item_data.quantity
        > variant.inventory.quantity
    ):
        raise AppException(
            message="Requested quantity exceeds available stock.",
            status_code=400,
        )

    item.quantity = (
        item_data.quantity
    )

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    return build_cart_response(
        db=db,
        cart_id=cart.id,
    )


def remove_cart_item(
    db: Session,
    user: User,
    item_id: int,
) -> None:
    cart = get_or_create_cart(
        db=db,
        user=user,
    )

    item = db.scalar(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    if item is None:
        raise AppException(
            message="Cart item not found.",
            status_code=404,
        )

    try:
        db.delete(item)
        db.commit()

    except Exception:
        db.rollback()
        raise


def clear_cart(
    db: Session,
    user: User,
) -> None:
    cart = get_or_create_cart(
        db=db,
        user=user,
    )

    try:
        db.execute(
            delete(CartItem).where(
                CartItem.cart_id
                == cart.id
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise