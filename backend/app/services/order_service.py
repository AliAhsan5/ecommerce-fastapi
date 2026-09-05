from decimal import Decimal

from sqlalchemy import (
    delete,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.core.exceptions import AppException
from app.models.address import Address
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.inventory import Inventory
from app.models.inventory_movement import (
    InventoryMovement,
)
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import (
    OrderStatusHistory,
)
from app.models.product_variant import (
    ProductVariant,
)
from app.models.user import User
from app.schemas.order import CheckoutRequest


def get_effective_price(
    variant: ProductVariant,
) -> Decimal:
    if variant.price_override is not None:
        return variant.price_override

    if variant.product.sale_price is not None:
        return variant.product.sale_price

    return variant.product.price


def get_existing_idempotent_order(
    db: Session,
    user_id: int,
    idempotency_key: str,
) -> Order | None:
    return db.scalar(
        select(Order)
        .where(
            Order.user_id == user_id,
            Order.idempotency_key
            == idempotency_key,
        )
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
            message="Shipping address not found.",
            status_code=404,
        )

    return address


def get_order_detail(
    db: Session,
    user: User,
    order_id: int,
) -> Order:
    order = db.scalar(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(
                Order.status_history
            ),
        )
        .where(
            Order.id == order_id,
            Order.user_id == user.id,
        )
    )

    if order is None:
        raise AppException(
            message="Order not found.",
            status_code=404,
        )

    return order


def checkout(
    db: Session,
    user: User,
    checkout_data: CheckoutRequest,
) -> Order:
    idempotency_key = (
        checkout_data.idempotency_key.strip()
    )

    existing_order = (
        get_existing_idempotent_order(
            db=db,
            user_id=user.id,
            idempotency_key=idempotency_key,
        )
    )

    if existing_order is not None:
        return get_order_detail(
            db=db,
            user=user,
            order_id=existing_order.id,
        )

    try:
        # Lock this user's cart so two checkout
        # requests cannot process it together.
        cart = db.scalar(
            select(Cart)
            .where(
                Cart.user_id == user.id
            )
            .with_for_update()
        )

        if cart is None:
            raise AppException(
                message="Cart is empty.",
                status_code=400,
            )

        # Important second idempotency check.
        # A concurrent request may have completed
        # while this request waited for the cart lock.
        existing_order = (
            get_existing_idempotent_order(
                db=db,
                user_id=user.id,
                idempotency_key=idempotency_key,
            )
        )

        if existing_order is not None:
            return get_order_detail(
                db=db,
                user=user,
                order_id=existing_order.id,
            )

        cart_items = list(
            db.scalars(
                select(CartItem)
                .where(
                    CartItem.cart_id
                    == cart.id
                )
                .order_by(
                    CartItem.variant_id
                )
            ).all()
        )

        if not cart_items:
            raise AppException(
                message="Cart is empty.",
                status_code=400,
            )

        address = get_owned_address(
            db=db,
            user=user,
            address_id=(
                checkout_data.address_id
            ),
        )

        validated_items = []
        order_subtotal = Decimal(
            "0.00"
        )

        for cart_item in cart_items:
            variant = db.scalar(
                select(ProductVariant)
                .options(
                    selectinload(
                        ProductVariant.product
                    )
                )
                .where(
                    ProductVariant.id
                    == cart_item.variant_id
                )
            )

            if variant is None:
                raise AppException(
                    message=(
                        "A cart product variant "
                        "no longer exists."
                    ),
                    status_code=400,
                )

            if not variant.is_active:
                raise AppException(
                    message=(
                        f"Variant {variant.sku} "
                        "is no longer available."
                    ),
                    status_code=400,
                )

            if not variant.product.is_active:
                raise AppException(
                    message=(
                        f"Product "
                        f"{variant.product.name} "
                        "is no longer available."
                    ),
                    status_code=400,
                )

            # Row-level PostgreSQL lock.
            inventory = db.scalar(
                select(Inventory)
                .where(
                    Inventory.variant_id
                    == variant.id
                )
                .with_for_update()
            )

            if inventory is None:
                raise AppException(
                    message=(
                        f"Inventory for "
                        f"{variant.sku} "
                        "was not found."
                    ),
                    status_code=400,
                )

            if (
                cart_item.quantity
                > inventory.quantity
            ):
                raise AppException(
                    message=(
                        f"Insufficient stock "
                        f"for {variant.sku}."
                    ),
                    status_code=400,
                )

            unit_price = (
                get_effective_price(
                    variant
                )
            )

            item_subtotal = (
                unit_price
                * cart_item.quantity
            )

            order_subtotal += (
                item_subtotal
            )

            validated_items.append(
                (
                    cart_item,
                    variant,
                    inventory,
                    unit_price,
                    item_subtotal,
                )
            )

        shipping_amount = Decimal(
            "0.00"
        )

        total_amount = (
            order_subtotal
            + shipping_amount
        )

        order = Order(
            user_id=user.id,
            shipping_address_id=address.id,
            idempotency_key=idempotency_key,

            recipient_name=(
                address.recipient_name
            ),
            phone=address.phone,
            address_line1=(
                address.address_line1
            ),
            address_line2=(
                address.address_line2
            ),
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,

            subtotal=order_subtotal,
            shipping_amount=(
                shipping_amount
            ),
            total_amount=total_amount,

            payment_method=(
                checkout_data.payment_method
            ),
            status="pending",
        )

        db.add(order)

        # Generate order.id before creating
        # order items/movements.
        db.flush()

        for (
            cart_item,
            variant,
            inventory,
            unit_price,
            item_subtotal,
        ) in validated_items:

            order_item = OrderItem(
                order_id=order.id,
                variant_id=variant.id,

                product_name=(
                    variant.product.name
                ),
                variant_name=variant.name,
                sku=variant.sku,

                unit_price=unit_price,
                quantity=(
                    cart_item.quantity
                ),
                subtotal=item_subtotal,
            )

            db.add(order_item)

            inventory.quantity -= (
                cart_item.quantity
            )

            movement = InventoryMovement(
                variant_id=variant.id,
                created_by_user_id=user.id,
                quantity_change=(
                    -cart_item.quantity
                ),
                balance_after=(
                    inventory.quantity
                ),
                reason=(
                    f"Order #{order.id} checkout"
                ),
            )

            db.add(movement)

        history = OrderStatusHistory(
            order_id=order.id,
            status="pending",
            changed_by_user_id=user.id,
        )

        db.add(history)

        # Cart is finalized only inside
        # the same transaction.
        db.execute(
            delete(CartItem).where(
                CartItem.cart_id == cart.id
            )
        )

        db.commit()

        return get_order_detail(
            db=db,
            user=user,
            order_id=order.id,
        )

    except IntegrityError:
        db.rollback()

        # Handles concurrent duplicate
        # idempotency-key requests safely.
        existing_order = (
            get_existing_idempotent_order(
                db=db,
                user_id=user.id,
                idempotency_key=idempotency_key,
            )
        )

        if existing_order is not None:
            return get_order_detail(
                db=db,
                user=user,
                order_id=existing_order.id,
            )

        raise

    except Exception:
        db.rollback()
        raise


def list_user_orders(
    db: Session,
    user: User,
    page: int,
    page_size: int,
) -> tuple[list[Order], int]:
    total = db.scalar(
        select(
            func.count(Order.id)
        ).where(
            Order.user_id == user.id
        )
    ) or 0

    orders = list(
        db.scalars(
            select(Order)
            .where(
                Order.user_id == user.id
            )
            .order_by(
                Order.created_at.desc()
            )
            .offset(
                (page - 1)
                * page_size
            )
            .limit(page_size)
        ).all()
    )

    return orders, total