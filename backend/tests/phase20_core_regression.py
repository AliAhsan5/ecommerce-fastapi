from __future__ import annotations

import importlib
import sys
import uuid
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.exceptions import AppException
from app.main import app

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

from app.schemas.order import CheckoutRequest

from app.services.admin_order_service import (
    ALLOWED_STATUS_TRANSITIONS,
    update_order_status,
)

from app.services.dashboard_service import (
    get_dashboard_metrics,
)

from app.services.order_service import checkout


# =========================================================
# GLOBAL TEST STATE
# =========================================================

client = TestClient(
    app,
    raise_server_exceptions=False,
)

TEST_EMAIL = (
    f"phase20-{uuid.uuid4().hex[:12]}"
    "@example.com"
)

TEST_PASSWORD = "Phase20!Backend123"

access_token: str | None = None
refresh_token: str | None = None

results: list[tuple[str, bool, str]] = []


# =========================================================
# HELPERS
# =========================================================

def record(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:

    results.append(
        (
            name,
            passed,
            detail,
        )
    )

    status = (
        "PASS"
        if passed
        else "FAIL"
    )

    print(
        f"[{status}] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )


def get_session_local():

    candidates = (
        "app.db.session",
        "app.database",
        "app.db.database",
    )

    for module_name in candidates:

        try:
            module = importlib.import_module(
                module_name
            )

            session_local = getattr(
                module,
                "SessionLocal",
                None,
            )

            if session_local is not None:
                return session_local

        except ImportError:
            continue

    raise RuntimeError(
        "SessionLocal could not be located."
    )


def resolve_schema(
    schema: dict[str, Any],
    openapi: dict[str, Any],
) -> dict[str, Any]:

    if "$ref" not in schema:
        return schema

    ref_name = (
        schema["$ref"]
        .split("/")[-1]
    )

    return (
        openapi["components"]
        ["schemas"]
        [ref_name]
    )


def sample_value(
    field_name: str,
    schema: dict[str, Any],
    openapi: dict[str, Any],
) -> Any:

    schema = resolve_schema(
        schema,
        openapi,
    )

    if "anyOf" in schema:

        choices = [
            choice
            for choice
            in schema["anyOf"]
            if choice.get("type")
            != "null"
        ]

        if choices:
            return sample_value(
                field_name,
                choices[0],
                openapi,
            )

    if "enum" in schema:
        return schema["enum"][0]

    field_lower = (
        field_name.lower()
    )

    special_values = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Phase 20 Customer",
        "name": "Phase 20 Customer",
        "phone": "03001234567",
        "address_line1": "Phase 20 Test Address",
        "address_line2": "",
        "city": "Karachi",
        "state": "Sindh",
        "postal_code": "75000",
        "country": "Pakistan",
        "payment_method": "cod",
        "idempotency_key": (
            f"phase20-{uuid.uuid4().hex}"
        ),
    }

    if field_lower in special_values:
        return special_values[field_lower]

    schema_type = schema.get(
        "type"
    )

    if schema_type == "integer":
        return 1

    if schema_type == "number":
        return 1

    if schema_type == "boolean":
        return True

    if schema_type == "array":
        return []

    if schema_type == "object":
        return {}

    return "phase20"


def request_payload(
    path: str,
    method: str,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:

    openapi = app.openapi()

    operation = (
        openapi["paths"]
        [path]
        [method.lower()]
    )

    request_body = operation.get(
        "requestBody",
        {}
    )

    content = request_body.get(
        "content",
        {}
    )

    json_content = content.get(
        "application/json",
        {}
    )

    schema = json_content.get(
        "schema",
        {}
    )

    schema = resolve_schema(
        schema,
        openapi,
    )

    properties = schema.get(
        "properties",
        {}
    )

    required = schema.get(
        "required",
        [],
    )

    payload: dict[str, Any] = {}

    for field_name in required:

        field_schema = properties.get(
            field_name,
            {},
        )

        payload[field_name] = (
            sample_value(
                field_name,
                field_schema,
                openapi,
            )
        )

    if overrides:

        for key, value in overrides.items():

            if (
                key in properties
                or not properties
            ):
                payload[key] = value

    return payload


def token_headers() -> dict[str, str]:

    if access_token is None:
        return {}

    return {
        "Authorization":
            f"Bearer {access_token}"
    }


# =========================================================
# TEST 1 — REGISTRATION
# =========================================================

def test_registration() -> bool:

    global access_token
    global refresh_token

    register_payload = request_payload(
        "/api/v1/auth/register",
        "post",
        {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name":
                "Phase 20 Customer",
        },
    )

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    if response.status_code not in (
        200,
        201,
    ):

        record(
            "1. Registration",
            False,
            (
                f"HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            ),
        )

        return False

    login_payload = request_payload(
        "/api/v1/auth/login",
        "post",
        {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    if login_response.status_code != 200:

        record(
            "1. Registration",
            False,
            (
                "Registration worked but "
                f"login returned "
                f"{login_response.status_code}: "
                f"{login_response.text}"
            ),
        )

        return False

    login_data = (
        login_response.json()
    )

    access_token = (
        login_data.get(
            "access_token"
        )
    )

    refresh_token = (
        login_data.get(
            "refresh_token"
        )
    )

    if not access_token:

        record(
            "1. Registration",
            False,
            "Login did not return access_token.",
        )

        return False

    me_response = client.get(
        "/api/v1/auth/me",
        headers=token_headers(),
    )

    passed = (
        me_response.status_code
        == 200
    )

    record(
        "1. Registration",
        passed,
        (
            "register -> login -> /auth/me"
            if passed
            else (
                f"/auth/me returned "
                f"{me_response.status_code}"
            )
        ),
    )

    return passed


# =========================================================
# TEST 2 — ADMIN AUTHORIZATION
# =========================================================

def test_admin_authorization() -> bool:

    logged_out = client.get(
        "/api/v1/admin/test"
    )

    customer = client.get(
        "/api/v1/admin/test",
        headers=token_headers(),
    )

    logged_out_blocked = (
        logged_out.status_code
        in (
            401,
            403,
        )
    )

    customer_forbidden = (
        customer.status_code
        == 403
    )

    passed = (
        logged_out_blocked
        and customer_forbidden
    )

    record(
        "2. Admin authorization",
        passed,
        (
            f"logged-out={logged_out.status_code}, "
            f"customer={customer.status_code}"
        ),
    )

    return passed


# =========================================================
# TEST 3 — CHECKOUT API
# =========================================================

def test_checkout() -> bool:

    checkout_payload = request_payload(
        "/api/v1/orders/checkout",
        "post",
        {
            "address_id": 1,
            "idempotency_key": (
                f"phase20-empty-cart-"
                f"{uuid.uuid4().hex}"
            ),
            "payment_method": "cod",
        },
    )

    logged_out = client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload,
    )

    authenticated = client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload,
        headers=token_headers(),
    )

    protected = (
        logged_out.status_code
        in (
            401,
            403,
        )
    )

    # Newly created Phase-20 customer has
    # no cart items, so checkout must reject
    # the request as a business validation.
    empty_cart_rejected = (
        authenticated.status_code
        == 400
    )

    passed = (
        protected
        and empty_cart_rejected
    )

    record(
        "3. Checkout",
        passed,
        (
            f"logged-out={logged_out.status_code}, "
            f"empty-cart={authenticated.status_code}"
        ),
    )

    return passed


# =========================================================
# TEST 4 — ROLLBACK BEHAVIOR
# =========================================================

class RollbackTrackingSession:

    def __init__(self):

        self.scalar_calls = 0
        self.rollback_calls = 0

    def scalar(
        self,
        statement,
    ):

        self.scalar_calls += 1

        # First scalar:
        # idempotent order lookup.
        #
        # Second scalar:
        # cart lookup.
        #
        # Both intentionally return None.
        return None

    def rollback(self):

        self.rollback_calls += 1


def test_rollback_behavior() -> bool:

    fake_db = (
        RollbackTrackingSession()
    )

    fake_user = SimpleNamespace(
        id=987654,
    )

    payload = request_payload(
        "/api/v1/orders/checkout",
        "post",
        {
            "address_id": 1,
            "idempotency_key": (
                "phase20-rollback-test"
            ),
            "payment_method": "cod",
        },
    )

    try:

        checkout_data = (
            CheckoutRequest.model_validate(
                payload
            )
        )

    except Exception as exc:

        record(
            "4. Rollback behavior",
            False,
            (
                "Could not build CheckoutRequest: "
                f"{exc}"
            ),
        )

        return False

    app_exception_seen = False

    try:

        checkout(
            db=fake_db,
            user=fake_user,
            checkout_data=checkout_data,
        )

    except AppException as exc:

        app_exception_seen = (
            exc.status_code
            == 400
        )

    except Exception as exc:

        record(
            "4. Rollback behavior",
            False,
            (
                f"Unexpected exception: "
                f"{type(exc).__name__}"
            ),
        )

        return False

    passed = (
        app_exception_seen
        and fake_db.rollback_calls
        == 1
    )

    record(
        "4. Rollback behavior",
        passed,
        (
            f"rollback_calls="
            f"{fake_db.rollback_calls}"
        ),
    )

    return passed


# =========================================================
# TEST 5 — ADMIN ORDER PROCESSING
# =========================================================

class FakeAdminOrderSession:

    def __init__(
        self,
        order,
    ):

        self.order = order
        self.added = []
        self.commit_calls = 0
        self.rollback_calls = 0

    def scalar(
        self,
        statement,
    ):

        return self.order

    def add(
        self,
        value,
    ):

        self.added.append(
            value
        )

    def commit(self):

        self.commit_calls += 1

    def rollback(self):

        self.rollback_calls += 1


def test_admin_order_processing() -> bool:

    expected_transitions = {
        "pending": {
            "confirmed",
            "cancelled",
        },
        "confirmed": {
            "processing",
            "cancelled",
        },
        "processing": {
            "shipped",
        },
        "shipped": {
            "delivered",
        },
        "delivered": set(),
        "cancelled": set(),
    }

    lifecycle_correct = (
        ALLOWED_STATUS_TRANSITIONS
        == expected_transitions
    )

    fake_order = SimpleNamespace(
        id=777001,
        status="pending",
    )

    fake_admin = SimpleNamespace(
        id=888001,
    )

    success_db = (
        FakeAdminOrderSession(
            fake_order
        )
    )

    success = False

    try:

        updated_order = (
            update_order_status(
                db=success_db,
                admin=fake_admin,
                order_id=fake_order.id,
                new_status="confirmed",
            )
        )

        added_types = {
            type(item).__name__
            for item
            in success_db.added
        }

        success = (
            updated_order.status
            == "confirmed"
            and success_db.commit_calls
            == 1
            and "OrderStatusHistory"
            in added_types
            and "AuditLog"
            in added_types
        )

    except Exception:
        success = False

    invalid_order = SimpleNamespace(
        id=777002,
        status="pending",
    )

    invalid_db = (
        FakeAdminOrderSession(
            invalid_order
        )
    )

    invalid_blocked = False

    try:

        update_order_status(
            db=invalid_db,
            admin=fake_admin,
            order_id=invalid_order.id,
            new_status="shipped",
        )

    except AppException as exc:

        invalid_blocked = (
            exc.status_code
            == 400
            and invalid_db.commit_calls
            == 0
        )

    passed = (
        lifecycle_correct
        and success
        and invalid_blocked
    )

    record(
        "5. Admin order processing",
        passed,
        (
            "pending -> confirmed allowed; "
            "pending -> shipped denied"
        ),
    )

    return passed


# =========================================================
# TEST 6 — DASHBOARD ACCURACY
# =========================================================

def normalize_decimal(
    value,
) -> Decimal:

    if value is None:
        return Decimal(
            "0.00"
        )

    return Decimal(
        str(value)
    )


def test_dashboard_accuracy() -> bool:

    SessionLocal = (
        get_session_local()
    )

    with SessionLocal() as db:

        metrics = (
            get_dashboard_metrics(
                db
            )
        )

        expected_customers = (
            db.scalar(
                select(
                    func.count(
                        User.id
                    )
                ).where(
                    User.role
                    == "customer"
                )
            )
            or 0
        )

        expected_products = (
            db.scalar(
                select(
                    func.count(
                        Product.id
                    )
                )
            )
            or 0
        )

        expected_orders = (
            db.scalar(
                select(
                    func.count(
                        Order.id
                    )
                )
            )
            or 0
        )

        expected_pending = (
            db.scalar(
                select(
                    func.count(
                        Order.id
                    )
                ).where(
                    Order.status
                    == "pending"
                )
            )
            or 0
        )

        expected_low_stock = (
            db.scalar(
                select(
                    func.count(
                        Inventory.id
                    )
                ).where(
                    Inventory.quantity
                    <=
                    Inventory.low_stock_threshold
                )
            )
            or 0
        )

        expected_sales = (
            db.scalar(
                select(
                    func.coalesce(
                        func.sum(
                            Order.total_amount
                        ),
                        0,
                    )
                ).where(
                    Order.status
                    == "delivered"
                )
            )
        )

        expected_recent = list(
            db.scalars(
                select(Order)
                .order_by(
                    Order.created_at.desc()
                )
                .limit(5)
            ).all()
        )

        actual_recent_ids = [
            order.id
            for order
            in metrics["recent_orders"]
        ]

        expected_recent_ids = [
            order.id
            for order
            in expected_recent
        ]

        passed = all(
            (
                metrics["customers"]
                == expected_customers,

                metrics["products"]
                == expected_products,

                metrics["orders"]
                == expected_orders,

                metrics["pending_orders"]
                == expected_pending,

                metrics["low_stock"]
                == expected_low_stock,

                normalize_decimal(
                    metrics["sales_total"]
                )
                ==
                normalize_decimal(
                    expected_sales
                ),

                actual_recent_ids
                == expected_recent_ids,
            )
        )

    record(
        "6. Dashboard accuracy",
        passed,
        (
            "customers/products/orders/"
            "pending/low-stock/sales/"
            "recent-orders verified"
        ),
    )

    return passed


# =========================================================
# CLEANUP
# =========================================================

def cleanup_phase20_user() -> None:

    try:

        SessionLocal = (
            get_session_local()
        )

        with SessionLocal() as db:

            user = db.scalar(
                select(User).where(
                    User.email
                    == TEST_EMAIL
                )
            )

            if user is None:
                return

            try:

                refresh_module = (
                    importlib.import_module(
                        "app.models.refresh_token"
                    )
                )

                RefreshToken = getattr(
                    refresh_module,
                    "RefreshToken",
                )

                db.execute(
                    delete(
                        RefreshToken
                    ).where(
                        RefreshToken.user_id
                        == user.id
                    )
                )

            except (
                ImportError,
                AttributeError,
            ):
                pass

            db.delete(
                user
            )

            db.commit()

    except Exception:

        # Cleanup failure must not hide
        # actual regression results.
        pass


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "================================="
    )

    print(
        "PHASE 20 CORE REGRESSION"
    )

    print(
        "================================="
    )

    try:

        registration_ok = (
            test_registration()
        )

        if registration_ok:

            test_admin_authorization()

            test_checkout()

        else:

            record(
                "2. Admin authorization",
                False,
                "Registration/login prerequisite failed.",
            )

            record(
                "3. Checkout",
                False,
                "Registration/login prerequisite failed.",
            )

        test_rollback_behavior()

        test_admin_order_processing()

        test_dashboard_accuracy()

    finally:

        cleanup_phase20_user()

    passed_count = sum(
        1
        for (
            _,
            passed,
            _,
        )
        in results
        if passed
    )

    total_count = len(
        results
    )

    print()
    print(
        "-----------------------------"
    )

    print(
        f"Tests passed: "
        f"{passed_count}/{total_count}"
    )

    print(
        "-----------------------------"
    )

    if (
        total_count == 6
        and passed_count == 6
    ):

        print(
            "PHASE 20 CORE REGRESSION PASSED"
        )

        sys.exit(
            0
        )

    print(
        "PHASE 20 CORE REGRESSION FAILED"
    )

    sys.exit(
        1
    )


if __name__ == "__main__":
    main()