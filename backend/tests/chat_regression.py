from app.db.session import SessionLocal
from app.schemas.chat import ChatHistoryMessage
from app.services.chat_service import process_chat_message


def print_result(
    test_name: str,
    passed: bool,
):
    status = "PASS" if passed else "FAIL"

    print(
        f"[{status}] {test_name}"
    )


def run_tests():

    db = SessionLocal()

    passed_tests = 0
    total_tests = 0

    try:

        # ---------------------------------
        # TEST 1 - Greeting
        # ---------------------------------

        total_tests += 1

        response = process_chat_message(
            db=db,
            message="Hello",
            history=[],
        )

        passed = (
            len(response.products) == 0
            and "shopping assistant"
            in response.reply.lower()
        )

        print_result(
            "Greeting",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 2 - General product query
        # ---------------------------------

        total_tests += 1

        response = process_chat_message(
            db=db,
            message="What products do you have?",
            history=[],
        )

        product_names = {
            product.name.lower()
            for product
            in response.products
        }

        passed = (
            "dior sauvage"
            in product_names
            and "ignis noir"
            in product_names
        )

        print_result(
            "General product search",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 3 - Budget search
        # ---------------------------------

        total_tests += 1

        response = process_chat_message(
            db=db,
            message=(
                "Mujhe 5000 ke andar "
                "perfume chahiye"
            ),
            history=[],
        )

        product_names = {
            product.name.lower()
            for product
            in response.products
        }

        passed = (
            "ignis noir"
            in product_names
            and "dior sauvage"
            not in product_names
        )

        print_result(
            "Budget search",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 4 - Specific stock query
        # ---------------------------------

        total_tests += 1

        response = process_chat_message(
            db=db,
            message=(
                "Is Dior Sauvage "
                "in stock?"
            ),
            history=[],
        )

        passed = (
            len(response.products) == 1
            and response.products[0].name
            == "Dior Sauvage"
            and response.products[
                0
            ].stock_quantity == 70
        )

        print_result(
            "Specific stock query",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 5 - Fake product
        # ---------------------------------

        total_tests += 1

        response = process_chat_message(
            db=db,
            message=(
                "Do you sell iPhone 25?"
            ),
            history=[],
        )

        passed = (
            len(response.products) == 0
            and "couldn't find"
            in response.reply.lower()
        )

        print_result(
            "Fake product protection",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 6 - First follow-up
        # ---------------------------------

        total_tests += 1

        history = [
            ChatHistoryMessage(
                role="user",
                content=(
                    "Is Dior Sauvage "
                    "in stock?"
                ),
            ),
            ChatHistoryMessage(
                role="assistant",
                content=(
                    "Yes, Dior Sauvage "
                    "100ml is in stock."
                ),
            ),
        ]

        response = process_chat_message(
            db=db,
            message="Iski price kya hai?",
            history=history,
        )

        passed = (
            len(response.products) == 1
            and response.products[0].name
            == "Dior Sauvage"
            and str(
                response.products[
                    0
                ].effective_price
            ) == "27000.00"
        )

        print_result(
            "Conversation follow-up",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # TEST 7 - Chained follow-up
        # ---------------------------------

        total_tests += 1

        history = [
            ChatHistoryMessage(
                role="user",
                content=(
                    "Is Dior Sauvage "
                    "in stock?"
                ),
            ),
            ChatHistoryMessage(
                role="assistant",
                content=(
                    "Yes, Dior Sauvage "
                    "is in stock."
                ),
            ),
            ChatHistoryMessage(
                role="user",
                content=(
                    "Iski price kya hai?"
                ),
            ),
            ChatHistoryMessage(
                role="assistant",
                content=(
                    "Dior Sauvage is "
                    "PKR 27,000."
                ),
            ),
        ]

        response = process_chat_message(
            db=db,
            message=(
                "Uska stock kitna hai?"
            ),
            history=history,
        )

        passed = (
            len(response.products) == 1
            and response.products[0].name
            == "Dior Sauvage"
            and response.products[
                0
            ].stock_quantity == 70
        )

        print_result(
            "Chained follow-up",
            passed,
        )

        if passed:
            passed_tests += 1


        # ---------------------------------
        # FINAL RESULT
        # ---------------------------------

        print()
        print(
            "----------------------------"
        )

        print(
            f"Tests passed: "
            f"{passed_tests}/{total_tests}"
        )

        print(
            "----------------------------"
        )

        if passed_tests == total_tests:

            print(
                "CHATBOT REGRESSION PASSED"
            )

        else:

            print(
                "CHATBOT REGRESSION FAILED"
            )

    finally:

        db.close()


if __name__ == "__main__":
    run_tests()