from __future__ import annotations

import os
import re
import subprocess
import sys

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


# ==========================================
# PATHS
# ==========================================

BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PROJECT_ROOT = (
    BACKEND_DIR.parent
)

TESTS_DIR = (
    BACKEND_DIR
    / "tests"
)

FRONTEND_DIR = (
    PROJECT_ROOT
    / "frontend"
)


# ==========================================
# RESULT STORAGE
# ==========================================

phase_results: list[
    tuple[str, bool, str]
] = []


successful_test_sources: list[
    tuple[Path, str]
] = []


# ==========================================
# HELPERS
# ==========================================

def add_result(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:

    phase_results.append(
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


def run_command(
    command: list[str],
    timeout: int = 300,
) -> tuple[
    bool,
    str,
]:

    env = os.environ.copy()

    existing_pythonpath = (
        env.get(
            "PYTHONPATH",
            "",
        )
    )

    env[
        "PYTHONPATH"
    ] = (
        str(BACKEND_DIR)
        + (
            os.pathsep
            + existing_pythonpath

            if existing_pythonpath
            else ""
        )
    )


    try:

        result = subprocess.run(
            command,
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )


    except subprocess.TimeoutExpired:

        return (
            False,
            "Command timed out.",
        )


    output = (
        result.stdout
        + result.stderr
    )


    failure_markers = (
        "[FAIL]",
        "REGRESSION FAILED",
        "TOOLS FAILED",
        "SECURITY FAILED",
        "HARDENING FAILED",
        "TEST SUITE FAILED",
    )


    marker_failure = any(
        marker.lower()
        in output.lower()
        for marker
        in failure_markers
    )


    passed = (
        result.returncode == 0
        and not marker_failure
    )


    return (
        passed,
        output,
    )


def discover_test_files() -> list[Path]:

    excluded = {
        "__init__.py",
        "conftest.py",
        "phase20_full_regression.py",
    }


    candidates: list[Path] = []


    for path in sorted(
        TESTS_DIR.glob(
            "*.py"
        )
    ):

        if (
            path.name
            in excluded
        ):
            continue


        normalized = (
            path.stem.lower()
        )


        if any(
            marker
            in normalized
            for marker
            in (
                "test",
                "regression",
                "security",
                "validation",
            )
        ):

            candidates.append(
                path
            )


    return candidates


def run_test_file(
    path: Path,
) -> tuple[
    bool,
    str,
]:

    if (
        path.name.startswith(
            "test_"
        )
    ):

        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            str(path),
        ]

    else:

        command = [
            sys.executable,
            str(path),
        ]


    timeout = (
        600
        if "ai"
        in path.name.lower()
        else 300
    )


    return run_command(
        command,
        timeout=timeout,
    )


def source_contains_groups(
    source: str,
    groups: tuple[
        tuple[str, ...],
        ...,
    ],
) -> bool:

    for group in groups:

        group_matched = any(
            re.search(
                pattern,
                source,
                flags=re.IGNORECASE,
            )
            is not None
            for pattern
            in group
        )


        if not group_matched:
            return False


    return True


def scenario_has_coverage(
    groups: tuple[
        tuple[str, ...],
        ...,
    ],
) -> bool:

    combined_source = "\n".join(
        (
            path.name
            + "\n"
            + source
        )
        for (
            path,
            source,
        )
        in successful_test_sources
    )


    return source_contains_groups(
        combined_source,
        groups,
    )


# ==========================================
# 1. HEALTH
# ==========================================

def test_health() -> None:

    try:

        client = TestClient(
            app,
            raise_server_exceptions=False,
        )

        response = client.get(
            "/health"
        )

        passed = (
            response.status_code
            == 200
        )

        add_result(
            "1. App health",
            passed,
            (
                f"HTTP "
                f"{response.status_code}"
            ),
        )


    except Exception as exc:

        add_result(
            "1. App health",
            False,
            type(exc).__name__,
        )


# ==========================================
# 2. MIGRATIONS
# ==========================================

def test_migrations() -> None:

    heads_ok, heads_output = (
        run_command(
            [
                sys.executable,
                "-m",
                "alembic",
                "heads",
            ]
        )
    )

    current_ok, current_output = (
        run_command(
            [
                sys.executable,
                "-m",
                "alembic",
                "current",
            ]
        )
    )


    revision_pattern = re.compile(
        r"\b[0-9a-f]{12}\b",
        flags=re.IGNORECASE,
    )


    head_revisions = set(
        revision_pattern.findall(
            heads_output
        )
    )

    current_revisions = set(
        revision_pattern.findall(
            current_output
        )
    )


    passed = (
        heads_ok
        and current_ok
        and bool(
            head_revisions
        )
        and (
            head_revisions
            == current_revisions
        )
    )


    detail = (
        "heads="
        + ",".join(
            sorted(
                head_revisions
            )
        )
        + " current="
        + ",".join(
            sorted(
                current_revisions
            )
        )
    )


    add_result(
        "2. Database migrations",
        passed,
        detail,
    )


# ==========================================
# EXISTING TEST SUITE EXECUTION
# ==========================================

def run_existing_tests() -> bool:

    print()
    print(
        "================================="
    )
    print(
        "RUNNING EXISTING TEST MODULES"
    )
    print(
        "================================="
    )


    test_files = (
        discover_test_files()
    )


    if not test_files:

        print(
            "[FAIL] No existing tests discovered."
        )

        return False


    all_passed = True


    for path in test_files:

        print()
        print(
            "---------------------------------"
        )

        print(
            f"Running: {path.name}"
        )

        print(
            "---------------------------------"
        )


        passed, output = (
            run_test_file(
                path
            )
        )


        if output.strip():

            print(
                output.rstrip()
            )


        if passed:

            try:

                source = (
                    path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                )

            except Exception:

                source = ""


            successful_test_sources.append(
                (
                    path,
                    source,
                )
            )


            print(
                f"[PASS] {path.name}"
            )


        else:

            all_passed = False

            print(
                f"[FAIL] {path.name}"
            )


    return all_passed


# ==========================================
# ROADMAP COVERAGE AUDIT
# ==========================================

SCENARIO_RULES = {

    "3. Registration": (
        (
            r"register",
            r"registration",
            r"/auth/register",
        ),
    ),


    "4. Login": (
        (
            r"login",
            r"/auth/login",
            r"authenticate_user",
        ),
    ),


    "5. Customer authorization": (
        (
            r"401",
            r"403",
            r"unauth",
            r"forbidden",
            r"logged-out",
        ),

        (
            r"cart",
            r"address",
            r"order",
            r"current_user",
        ),
    ),


    "6. Admin authorization": (
        (
            r"admin",
        ),

        (
            r"403",
            r"denied",
            r"forbidden",
            r"require_admin",
            r"current_admin",
        ),
    ),


    "7. Category / brand": (
        (
            r"categor",
        ),

        (
            r"brand",
        ),
    ),


    "8. Product catalog": (
        (
            r"product",
        ),

        (
            r"search",
            r"filter",
            r"pagination",
            r"/products",
        ),
    ),


    "9. Inventory": (
        (
            r"inventory",
            r"stock",
            r"stock_quantity",
        ),
    ),


    "10. Cart": (
        (
            r"\bcart\b",
            r"/cart",
            r"cart_service",
        ),
    ),


    "11. Checkout": (
        (
            r"checkout",
            r"/orders/checkout",
            r"checkout_service",
        ),
    ),


    "12. Rollback behavior": (
        (
            r"rollback",
            r"roll back",
            r"simulated failure",
            r"transaction failure",
        ),
    ),


    "13. Order ownership": (
        (
            r"foreign",
            r"non-owned",
            r"ownership",
            r"another customer",
            r"current_user",
        ),

        (
            r"order",
        ),
    ),


    "14. Admin order processing": (
        (
            r"admin",
        ),

        (
            r"order",
        ),

        (
            r"status",
            r"transition",
            r"processing",
            r"confirmed",
            r"shipped",
        ),
    ),


    "15. Dashboard accuracy": (
        (
            r"dashboard",
        ),

        (
            r"sales",
            r"pending",
            r"low.?stock",
            r"metric",
            r"customers",
            r"recent.?orders",
        ),
    ),


    "16. AI product search": (
        (
            r"ai_tools",
            r"tool_assisted",
            r"search_products",
            r"ai product",
        ),

        (
            r"product",
        ),
    ),


    "17. AI private-order authorization": (
        (
            r"chat/order",
            r"order_assistant",
            r"ai_order",
            r"order ai",
        ),

        (
            r"logged-out",
            r"foreign",
            r"current_user",
            r"another customer",
            r"authenticated",
        ),
    ),
}


def audit_scenario_coverage() -> None:

    print()
    print(
        "================================="
    )

    print(
        "ROADMAP COVERAGE AUDIT"
    )

    print(
        "================================="
    )


    for (
        scenario_name,
        groups,
    ) in SCENARIO_RULES.items():

        passed = (
            scenario_has_coverage(
                groups
            )
        )


        add_result(
            scenario_name,
            passed,
            (
                "covered by passed "
                "automated test source"
                if passed
                else
                "no passed automated "
                "coverage detected"
            ),
        )


# ==========================================
# 18. FRONTEND CRITICAL JOURNEY
# ==========================================

def test_frontend_contract() -> None:

    required_files = [
        FRONTEND_DIR
        / "index.html",

        FRONTEND_DIR
        / "login.html",

        FRONTEND_DIR
        / "product.html",

        FRONTEND_DIR
        / "cart.html",

        FRONTEND_DIR
        / "checkout.html",

        FRONTEND_DIR
        / "orders.html",

        FRONTEND_DIR
        / "order-detail.html",

        FRONTEND_DIR
        / "js"
        / "api.js",

        FRONTEND_DIR
        / "js"
        / "products.js",

        FRONTEND_DIR
        / "js"
        / "cart.js",

        FRONTEND_DIR
        / "js"
        / "checkout.js",

        FRONTEND_DIR
        / "js"
        / "orders.js",

        FRONTEND_DIR
        / "js"
        / "chat-widget.js",
    ]


    missing = [
        str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
        for path
        in required_files
        if not path.exists()
    ]


    api_file = (
        FRONTEND_DIR
        / "js"
        / "api.js"
    )


    api_contract_ok = False


    if api_file.exists():

        api_source = (
            api_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )


        api_contract_ok = (
            "apiRequest"
            in api_source

            and
            "checkout"
            in api_source.lower()

            and
            "cart"
            in api_source.lower()

            and
            "order"
            in api_source.lower()
        )


    passed = (
        not missing
        and api_contract_ok
    )


    detail = (
        "critical pages + API contract present"
        if passed
        else (
            "missing="
            + (
                ", ".join(
                    missing
                )
                if missing
                else "none"
            )
            + (
                "; api.js contract incomplete"
                if not api_contract_ok
                else ""
            )
        )
    )


    add_result(
        "18. Frontend critical journey contract",
        passed,
        detail,
    )


# ==========================================
# PYTHON SYNTAX CHECK
# ==========================================

def test_backend_syntax() -> bool:

    passed, output = (
        run_command(
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "app",
                "tests",
            ]
        )
    )


    print()
    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "Backend Python syntax"
    )


    if (
        not passed
        and output
    ):

        print(
            output
        )


    return passed


# ==========================================
# FINAL SUMMARY
# ==========================================

def print_final_summary(
    existing_tests_passed: bool,
    syntax_passed: bool,
) -> None:

    print()
    print(
        "================================="
    )

    print(
        "PHASE 20 FINAL SUMMARY"
    )

    print(
        "================================="
    )


    for (
        name,
        passed,
        _,
    ) in phase_results:

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"{status:4} | {name}"
        )


    roadmap_passed = all(
        passed
        for (
            _,
            passed,
            _,
        )
        in phase_results
    )


    overall_passed = (
        roadmap_passed
        and existing_tests_passed
        and syntax_passed
    )


    print()
    print(
        "---------------------------------"
    )

    print(
        f"Roadmap scenarios passed: "
        f"{sum(1 for _, passed, _ in phase_results if passed)}"
        f"/{len(phase_results)}"
    )

    print(
        "Existing tests: "
        + (
            "PASS"
            if existing_tests_passed
            else "FAIL"
        )
    )

    print(
        "Python syntax: "
        + (
            "PASS"
            if syntax_passed
            else "FAIL"
        )
    )

    print(
        "---------------------------------"
    )


    if overall_passed:

        print(
            "PHASE 20 FULL REGRESSION PASSED"
        )

        sys.exit(
            0
        )


    print(
        "PHASE 20 FULL REGRESSION FAILED"
    )

    print()
    print(
        "Any FAIL above identifies the "
        "exact regression/coverage gap "
        "that must be fixed."
    )

    sys.exit(
        1
    )


# ==========================================
# MAIN
# ==========================================

def main() -> None:

    print(
        "================================="
    )

    print(
        "PHASE 20 - FULL AUTOMATED "
        "REGRESSION SUITE"
    )

    print(
        "================================="
    )


    syntax_passed = (
        test_backend_syntax()
    )


    test_health()

    test_migrations()


    existing_tests_passed = (
        run_existing_tests()
    )


    audit_scenario_coverage()

    test_frontend_contract()


    print_final_summary(
        existing_tests_passed=(
            existing_tests_passed
        ),

        syntax_passed=(
            syntax_passed
        ),
    )


if __name__ == "__main__":
    main()