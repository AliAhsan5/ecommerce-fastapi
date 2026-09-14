from unittest.mock import patch

from fastapi.testclient import (
    TestClient,
)
from sqlalchemy import select

from app.api.deps import (
    get_current_user,
)
from app.db.session import (
    SessionLocal,
)
from app.main import (
    app,
)
from app.models.order import (
    Order,
)
from app.models.user import (
    User,
)


client = TestClient(
    app
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

    passed_tests = 0
    total_tests = 0


    # ------------------------------
    # TEST 1
    # Logged-out blocked
    # ------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat/order",
        json={
            "message": (
                "What is my latest order?"
            ),
            "history": [],
        },
    )

    passed = (
        response.status_code
        in (
            401,
            403,
        )
    )

    if show(
        "Logged-out order AI blocked",
        passed,
    ):
        passed_tests += 1


    # ------------------------------
    # Obtain real customer fixture
    # ------------------------------

    db = SessionLocal()

    try:

        order = db.scalar(
            select(Order)
            .order_by(
                Order.id.asc()
            )
        )

        if order is None:

            print(
                "[FAIL] No order available "
                "for authenticated route test."
            )

            return


        user = db.get(
            User,
            order.user_id,
        )


        # ------------------------------
        # TEST 2
        # Authenticated dependency
        # reaches assistant
        # ------------------------------

        total_tests += 1


        def override_user():
            return user


        app.dependency_overrides[
            get_current_user
        ] = override_user


        with patch(
            (
                "app.api.v1.chat."
                "generate_order_assistant_response"
            ),
            return_value=(
                "Authenticated order assistant OK"
            ),
        ):

            response = client.post(
                "/api/v1/chat/order",
                json={
                    "message": (
                        "What is my latest order?"
                    ),
                    "history": [],
                },
            )


        passed = (
            response.status_code
            == 200
            and response.json()[
                "reply"
            ]
            == (
                "Authenticated order assistant OK"
            )
        )

        if show(
            "Authenticated order route works",
            passed,
        ):
            passed_tests += 1


    finally:

        app.dependency_overrides.clear()

        db.close()


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
            "ORDER AI API SECURITY PASSED"
        )

    else:

        print(
            "ORDER AI API SECURITY FAILED"
        )


if __name__ == "__main__":
    run_tests()