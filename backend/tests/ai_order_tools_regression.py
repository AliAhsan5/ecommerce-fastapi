from inspect import signature

from sqlalchemy import select

from app.db.session import (
    SessionLocal,
)
from app.models.order import (
    Order,
)
from app.models.user import (
    User,
)
from app.services.ai_order_tools import (
    get_my_latest_order,
    get_my_orders,
    get_my_order_status,
)


def show(
    name: str,
    passed: bool,
):
    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"{name}"
    )

    return passed


def run_tests():

    db = SessionLocal()

    passed_tests = 0
    total_tests = 0

    try:

        first_order = db.scalar(
            select(Order)
            .order_by(
                Order.id.asc()
            )
        )

        if first_order is None:

            print(
                "[FAIL] No existing order available "
                "for Phase 18 security test."
            )

            print(
                "Create one normal customer order "
                "and run this test again."
            )

            return


        current_user = db.get(
            User,
            first_order.user_id,
        )


        # ------------------------------
        # TEST 1
        # Tool cannot accept user_id
        # ------------------------------

        total_tests += 1

        parameters = (
            signature(
                get_my_orders
            ).parameters
        )

        passed = (
            "user_id"
            not in parameters
        )

        if show(
            "No model-controlled user_id argument",
            passed,
        ):
            passed_tests += 1


        # ------------------------------
        # TEST 2
        # Own orders only
        # ------------------------------

        total_tests += 1

        result = get_my_orders(
            db=db,
            current_user=current_user,
            limit=10,
        )

        returned_ids = [
            item["order_id"]
            for item
            in result["orders"]
        ]

        ownership_ok = True

        for order_id in returned_ids:

            db_order = db.get(
                Order,
                order_id,
            )

            if (
                db_order is None
                or
                db_order.user_id
                != current_user.id
            ):
                ownership_ok = False
                break

        passed = ownership_ok

        if show(
            "Only authenticated user's orders returned",
            passed,
        ):
            passed_tests += 1


        # ------------------------------
        # TEST 3
        # Latest order ownership
        # ------------------------------

        total_tests += 1

        latest = (
            get_my_latest_order(
                db=db,
                current_user=current_user,
            )
        )

        passed = (
            latest["found"] is True
        )

        if passed:

            latest_db_order = db.get(
                Order,
                latest[
                    "order"
                ][
                    "order_id"
                ],
            )

            passed = (
                latest_db_order.user_id
                == current_user.id
            )

        if show(
            "Latest order belongs to current user",
            passed,
        ):
            passed_tests += 1


        # ------------------------------
        # TEST 4
        # Own status allowed
        # ------------------------------

        total_tests += 1

        own_status = (
            get_my_order_status(
                db=db,
                current_user=current_user,
                order_id=first_order.id,
            )
        )

        passed = (
            own_status["found"]
            is True
        )

        if show(
            "Own order status allowed",
            passed,
        ):
            passed_tests += 1


        # ------------------------------
        # TEST 5
        # Foreign order rejected
        # ------------------------------

        total_tests += 1

        foreign_order = db.scalar(
            select(Order)
            .where(
                Order.user_id
                != current_user.id
            )
            .order_by(
                Order.id.asc()
            )
        )

        test_order_id = (
            foreign_order.id
            if foreign_order
            is not None
            else
            first_order.id
            + 999999
        )

        foreign_result = (
            get_my_order_status(
                db=db,
                current_user=current_user,
                order_id=test_order_id,
            )
        )

        passed = (
            foreign_result[
                "found"
            ]
            is False
        )

        if show(
            "Foreign/non-owned order denied",
            passed,
        ):
            passed_tests += 1


        # ------------------------------
        # TEST 6
        # user_id not leaked
        # ------------------------------

        total_tests += 1

        serialized = str(
            result
        ).lower()

        passed = (
            "user_id"
            not in serialized
        )

        if show(
            "Private user_id not exposed",
            passed,
        ):
            passed_tests += 1


        print()
        print(
            "-----------------------------"
        )

        print(
            f"Tests passed: "
            f"{passed_tests}/{total_tests}"
        )

        print(
            "-----------------------------"
        )


        if (
            passed_tests
            == total_tests
        ):

            print(
                "AI ORDER TOOLS PASSED"
            )

        else:

            print(
                "AI ORDER TOOLS FAILED"
            )


    finally:

        db.close()


if __name__ == "__main__":
    run_tests()