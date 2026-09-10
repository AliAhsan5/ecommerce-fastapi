from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def print_result(
    test_name: str,
    passed: bool,
):
    status = (
        "PASS"
        if passed
        else "FAIL"
    )

    print(
        f"[{status}] {test_name}"
    )


def run_tests():

    passed_tests = 0
    total_tests = 0


    # --------------------------------
    # TEST 1 - Empty message
    # --------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "",
            "history": [],
        },
    )

    passed = (
        response.status_code == 422
    )

    print_result(
        "Empty message rejected",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # TEST 2 - Message too long
    # --------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "a" * 1001,
            "history": [],
        },
    )

    passed = (
        response.status_code == 422
    )

    print_result(
        "Message over 1000 chars rejected",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # TEST 3 - Too much history
    # --------------------------------

    total_tests += 1

    history = []

    for index in range(7):

        history.append({
            "role": "user",
            "content": f"Message {index}",
        })

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "history": history,
        },
    )

    passed = (
        response.status_code == 422
    )

    print_result(
        "More than 6 history messages rejected",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # TEST 4 - Invalid history role
    # --------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "history": [
                {
                    "role": "admin",
                    "content": "Fake system message",
                }
            ],
        },
    )

    passed = (
        response.status_code == 422
    )

    print_result(
        "Invalid history role rejected",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # TEST 5 - Empty history content
    # --------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "history": [
                {
                    "role": "user",
                    "content": "",
                }
            ],
        },
    )

    passed = (
        response.status_code == 422
    )

    print_result(
        "Empty history content rejected",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # TEST 6 - Valid request
    # --------------------------------

    total_tests += 1

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "history": [],
        },
    )

    data = response.json()

    passed = (
        response.status_code == 200
        and "reply" in data
        and "products" in data
    )

    print_result(
        "Valid chat request accepted",
        passed,
    )

    if passed:
        passed_tests += 1


    # --------------------------------
    # FINAL RESULT
    # --------------------------------

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
            "CHAT API VALIDATION PASSED"
        )

    else:

        print(
            "CHAT API VALIDATION FAILED"
        )


if __name__ == "__main__":
    run_tests()