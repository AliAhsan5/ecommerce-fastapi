from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.core.config import get_settings
from app.core.hardening import reset_hardening_rate_limits
from app.db.session import SessionLocal
from app.main import app


TEST_CRASH_PATH = "/__phase19_crash"


if not any(
    getattr(route, "path", None) == TEST_CRASH_PATH
    for route in app.routes
):

    @app.get(TEST_CRASH_PATH)
    def phase19_test_crash():
        raise RuntimeError(
            "PHASE19_PRIVATE_TEST_MARKER"
        )


client = TestClient(
    app,
    raise_server_exceptions=False,
)


def show(
    name: str,
    passed: bool,
) -> bool:

    status = (
        "PASS"
        if passed
        else "FAIL"
    )

    print(
        f"[{status}] {name}"
    )

    return passed


def run_tests():

    passed_tests = 0
    total_tests = 0

    # ==============================
    # TEST 1 - HEALTH
    # ==============================

    total_tests += 1

    response = client.get(
        "/health"
    )

    passed = (
        response.status_code == 200
    )

    if show(
        "Health endpoint",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 2 - SECURITY HEADERS
    # ==============================

    total_tests += 1

    headers = response.headers

    passed = (
        headers.get(
            "x-content-type-options"
        ) == "nosniff"
        and headers.get(
            "x-frame-options"
        ) == "DENY"
        and headers.get(
            "referrer-policy"
        ) == "no-referrer"
        and bool(
            headers.get(
                "x-request-id"
            )
        )
    )

    if show(
        "Security headers",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 3 - READINESS
    # ==============================

    total_tests += 1

    response = client.get(
        "/ready"
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and data.get(
            "status"
        ) == "ready"
        and data.get(
            "database"
        ) == "ok"
    )

    if show(
        "Database readiness",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 4 - CORS CONFIG
    # ==============================

    total_tests += 1

    settings = get_settings()

    passed = (
        "*"
        not in settings.cors_origins
    )

    if show(
        "CORS wildcard disabled",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 5 - ALLOWED CORS
    # ==============================

    total_tests += 1

    response = client.options(
        "/api/v1/products",
        headers={
            "Origin":
                "http://127.0.0.1:5500",

            "Access-Control-Request-Method":
                "GET",
        },
    )

    passed = (
        response.headers.get(
            "access-control-allow-origin"
        )
        == "http://127.0.0.1:5500"
    )

    if show(
        "Allowed CORS origin",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 6 - DISALLOWED CORS
    # ==============================

    total_tests += 1

    response = client.options(
        "/api/v1/products",
        headers={
            "Origin":
                "https://evil.example",

            "Access-Control-Request-Method":
                "GET",
        },
    )

    passed = (
        response.headers.get(
            "access-control-allow-origin"
        )
        is None
    )

    if show(
        "Unknown CORS origin blocked",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 7 - AUTHORIZATION MATRIX
    # ==============================

    total_tests += 1

    checks = []

    for path in (
        "/api/v1/cart",
        "/api/v1/addresses",
        "/api/v1/orders",
    ):

        response = client.get(
            path
        )

        checks.append(
            response.status_code
            in (
                401,
                403,
            )
        )

    response = client.post(
        "/api/v1/chat/order",
        json={
            "message":
                "Show me my orders",

            "history": [],
        },
    )

    checks.append(
        response.status_code
        in (
            401,
            403,
        )
    )

    passed = all(
        checks
    )

    if show(
        "Logged-out authorization matrix",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 8 - LOGIN RATE LIMIT
    # ==============================

    total_tests += 1

    reset_hardening_rate_limits()

    for _ in range(
        10
    ):

        client.post(
            "/api/v1/auth/login",
            json={
                "email":
                    "nobody@example.com",

                "password":
                    "WrongPassword123!",
            },
        )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email":
                "nobody@example.com",

            "password":
                "WrongPassword123!",
        },
    )

    passed = (
        response.status_code == 429
    )

    if show(
        "Login rate limiting",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 9 - REQUEST SIZE LIMIT
    # ==============================

    total_tests += 1

    huge_message = (
        "x"
        * (
            1024 * 1024
            + 100
        )
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message":
                huge_message,

            "history": [],
        },
    )

    passed = (
        response.status_code == 413
    )

    if show(
        "Large request blocked",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 10 - PAGINATION LIMIT
    # ==============================

    total_tests += 1

    response = client.get(
        "/api/v1/products?page_size=100000"
    )

    passed = (
        response.status_code == 422
    )

    if show(
        "Large pagination blocked",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 11 - SAFE 500 RESPONSE
    # ==============================

    total_tests += 1

    response = client.get(
        TEST_CRASH_PATH
    )

    body = response.text.lower()

    passed = (
        response.status_code == 500
        and
        "internal server error"
        in body
        and
        "phase19_private_test_marker"
        not in body
        and bool(
            response.headers.get(
                "x-request-id"
            )
        )
    )

    if show(
        "Unexpected errors sanitized",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # TEST 12 - DATABASE INDEXES
    # ==============================

    total_tests += 1

    expected_indexes = {
        "orders": {
            "ix_orders_user_created_at",
            "ix_orders_status_created_at",
        },

        "products": {
            "ix_products_active_category",
            "ix_products_active_brand",
        },

        "product_variants": {
            "ix_product_variants_product_active",
        },

        "addresses": {
            "ix_addresses_user_id",
        },

        "order_items": {
            "ix_order_items_order_id",
        },
    }

    db = SessionLocal()

    try:

        inspector = inspect(
            db.get_bind()
        )

        table_names = set(
            inspector.get_table_names()
        )

        index_checks = []

        for (
            table_name,
            required_indexes,
        ) in expected_indexes.items():

            if (
                table_name
                not in table_names
            ):

                index_checks.append(
                    False
                )

                continue

            actual_indexes = {
                index["name"]
                for index
                in inspector.get_indexes(
                    table_name
                )
                if index.get(
                    "name"
                )
            }

            index_checks.append(
                required_indexes.issubset(
                    actual_indexes
                )
            )

        passed = all(
            index_checks
        )

    finally:

        db.close()

    if show(
        "Hardening DB indexes",
        passed,
    ):
        passed_tests += 1

    # ==============================
    # FINAL RESULT
    # ==============================

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
            "PHASE 19 HARDENING PASSED"
        )

    else:

        print(
            "PHASE 19 HARDENING FAILED"
        )


if __name__ == "__main__":
    run_tests()