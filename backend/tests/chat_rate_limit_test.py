from fastapi.testclient import TestClient

from app.core.chat_rate_limit import (
    request_history,
)
from app.main import app


client = TestClient(app)


def run_test():

    request_history.clear()

    passed_requests = 0


    for _ in range(10):

        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Hello",
                "history": [],
            },
        )

        if response.status_code == 200:
            passed_requests += 1


    blocked_response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "history": [],
        },
    )


    first_ten_passed = (
        passed_requests == 10
    )

    eleventh_blocked = (
        blocked_response.status_code
        == 429
    )


    print(
        "[PASS] First 10 requests allowed"
        if first_ten_passed
        else
        "[FAIL] First 10 requests allowed"
    )

    print(
        "[PASS] 11th request blocked"
        if eleventh_blocked
        else
        "[FAIL] 11th request blocked"
    )


    print()


    if (
        first_ten_passed
        and eleventh_blocked
    ):
        print(
            "CHAT RATE LIMIT PASSED"
        )
    else:
        print(
            "CHAT RATE LIMIT FAILED"
        )


if __name__ == "__main__":
    run_test()