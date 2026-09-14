from app.db.session import SessionLocal

from app.services.ai_product_tools import (
    check_stock,
    compare_products,
    get_product_detail,
    search_products,
)
from app.services.ai_tool_service import (
    generate_tool_assisted_response,
)


def print_result(
    name: str,
    passed: bool,
):
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

    db = SessionLocal()

    passed_tests = 0
    total_tests = 0

    try:

        # ---------------------------------
        # TEST 1 - Product Search Tool
        # ---------------------------------

        total_tests += 1

        search_result = search_products(
            db=db,
            search="Dior",
        )

        passed = (
            search_result["returned"] >= 1
            and any(
                product["name"]
                == "Dior Sauvage"
                for product
                in search_result["products"]
            )
        )

        if print_result(
            "Product search tool",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 2 - Product Detail Tool
        # ---------------------------------

        total_tests += 1

        detail = get_product_detail(
            db=db,
            product_id=1,
        )

        passed = (
            detail["name"]
            == "Dior Sauvage"
            and len(
                detail["variants"]
            ) > 0
            and str(
                detail["variants"][0][
                    "effective_price"
                ]
            ) == "27000.00"
        )

        if print_result(
            "Product detail tool",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 3 - Stock Tool
        # ---------------------------------

        total_tests += 1

        stock = check_stock(
            db=db,
            variant_id=1,
        )

        passed = (
            stock["stock_quantity"]
            == 70
            and stock["availability"]
            == "in_stock"
        )

        if print_result(
            "Stock tool",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 4 - Comparison Tool
        # ---------------------------------

        total_tests += 1

        comparison = compare_products(
            db=db,
            product_ids=[
                1,
                2,
            ],
        )

        comparison_products = {
            product["name"].lower():
            product
            for product
            in comparison["products"]
        }

        dior = comparison_products.get(
            "dior sauvage"
        )

        ignis = comparison_products.get(
            "ignis noir"
        )

        passed = (
            comparison[
                "comparison_count"
            ] == 2
            and dior is not None
            and ignis is not None
            and str(
                dior["variants"][0][
                    "effective_price"
                ]
            ) == "27000.00"
            and dior[
                "variants"
            ][0][
                "stock_quantity"
            ] == 70
            and str(
                ignis["variants"][0][
                    "effective_price"
                ]
            ) == "2000.00"
            and ignis[
                "variants"
            ][0][
                "stock_quantity"
            ] == 50
        )

        if print_result(
            "Comparison tool",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 5 - AI Tool Calling Smoke
        # ---------------------------------

        total_tests += 1

        ai_response = (
            generate_tool_assisted_response(
                db=db,
                message=(
                    "Is Dior Sauvage "
                    "in stock?"
                ),
            )
        )

        passed = (
            isinstance(
                ai_response,
                str,
            )
            and len(
                ai_response.strip()
            ) > 0
        )

        if print_result(
            "AI tool calling smoke test",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 6 - AI Comparison Smoke
        # ---------------------------------

        total_tests += 1

        ai_response = (
            generate_tool_assisted_response(
                db=db,
                message=(
                    "Compare Dior Sauvage "
                    "and Ignis Noir"
                ),
            )
        )

        normalized = (
            ai_response
            .lower()
        )

        passed = (
            len(
                ai_response.strip()
            ) > 0
            and "dior"
            in normalized
            and "ignis"
            in normalized
        )

        if print_result(
            "AI comparison smoke test",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # TEST 7 - Verified Grounding Source
        # ---------------------------------

        total_tests += 1

        verified = get_product_detail(
            db=db,
            product_id=1,
        )

        variant = (
            verified["variants"][0]
        )

        passed = (
            verified["name"]
            == "Dior Sauvage"
            and str(
                variant[
                    "effective_price"
                ]
            ) == "27000.00"
            and variant[
                "stock_quantity"
            ] == 70
        )

        if print_result(
            "Verified grounding source",
            passed,
        ):
            passed_tests += 1


        # ---------------------------------
        # FINAL RESULT
        # ---------------------------------

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
                "AI PRODUCT TOOLS PASSED"
            )

        else:

            print(
                "AI PRODUCT TOOLS FAILED"
            )

    finally:

        db.close()


if __name__ == "__main__":
    run_tests()