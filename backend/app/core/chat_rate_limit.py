import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import (
    HTTPException,
    Request,
    status,
)


MAX_REQUESTS = 10
WINDOW_SECONDS = 60


request_history: dict[
    str,
    deque[float],
] = defaultdict(deque)


rate_limit_lock = Lock()


def get_client_ip(
    request: Request,
) -> str:

    if request.client is None:
        return "unknown"

    return request.client.host


def enforce_chat_rate_limit(
    request: Request,
) -> None:

    client_ip = get_client_ip(
        request
    )

    current_time = time.monotonic()

    window_start = (
        current_time
        - WINDOW_SECONDS
    )


    with rate_limit_lock:

        timestamps = request_history[
            client_ip
        ]


        while (
            timestamps
            and timestamps[0]
            <= window_start
        ):
            timestamps.popleft()


        if (
            len(timestamps)
            >= MAX_REQUESTS
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail=(
                    "Too many chat requests. "
                    "Please try again shortly."
                ),
            )


        timestamps.append(
            current_time
        )