import logging
import time
import uuid

from collections import (
    defaultdict,
    deque,
)
from threading import Lock

from fastapi import Request
from sqlalchemy import text
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import (
    JSONResponse,
    Response,
)

from app.db.session import (
    SessionLocal,
)


logger = logging.getLogger(
    __name__
)


MAX_REQUEST_BODY_BYTES = (
    1024 * 1024
)

MAX_PAGE_SIZE = 100


AUTH_RATE_LIMITS = {
    (
        "POST",
        "/api/v1/auth/login",
    ): (
        10,
        60,
    ),

    (
        "POST",
        "/api/v1/auth/register",
    ): (
        5,
        60,
    ),

    (
        "POST",
        "/api/v1/auth/refresh",
    ): (
        20,
        60,
    ),

    (
        "POST",
        "/api/v1/auth/change-password",
    ): (
        5,
        60,
    ),
}


_rate_history = defaultdict(
    deque
)

_rate_lock = Lock()


def reset_hardening_rate_limits():
    """
    Used by automated tests.
    """

    with _rate_lock:
        _rate_history.clear()


def get_client_key(
    request: Request,
) -> str:

    if (
        request.client
        and request.client.host
    ):
        return request.client.host

    return "unknown"


def is_rate_limited(
    request: Request,
) -> tuple[
    bool,
    int | None,
]:

    rule = AUTH_RATE_LIMITS.get(
        (
            request.method.upper(),
            request.url.path,
        )
    )

    if rule is None:
        return (
            False,
            None,
        )

    max_requests, window_seconds = (
        rule
    )

    now = time.monotonic()

    client_key = get_client_key(
        request
    )

    history_key = (
        request.method.upper(),
        request.url.path,
        client_key,
    )


    with _rate_lock:

        history = _rate_history[
            history_key
        ]

        while (
            history
            and
            now - history[0]
            >= window_seconds
        ):
            history.popleft()


        if (
            len(history)
            >= max_requests
        ):
            return (
                True,
                window_seconds,
            )


        history.append(
            now
        )


    return (
        False,
        None,
    )


def check_pagination_limit(
    request: Request,
) -> bool:

    value = (
        request.query_params.get(
            "page_size"
        )
    )

    if value is None:
        return True


    try:

        page_size = int(
            value
        )

    except ValueError:
        return True


    return (
        page_size
        <= MAX_PAGE_SIZE
    )


def check_request_size(
    request: Request,
) -> bool:

    content_length = (
        request.headers.get(
            "content-length"
        )
    )

    if content_length is None:
        return True


    try:

        size = int(
            content_length
        )

    except ValueError:
        return False


    return (
        size
        <= MAX_REQUEST_BODY_BYTES
    )


def database_readiness() -> bool:

    try:

        with SessionLocal() as db:

            db.execute(
                text(
                    "SELECT 1"
                )
            )

        return True

    except Exception as exc:

        logger.error(
            (
                "Database readiness "
                "check failed. type=%s"
            ),
            type(exc).__name__,
        )

        return False


class SecurityHardeningMiddleware(
    BaseHTTPMiddleware
):

    def __init__(
        self,
        app,
        environment: str = (
            "development"
        ),
    ):

        super().__init__(
            app
        )

        self.environment = (
            environment
            .strip()
            .lower()
        )


    def add_security_headers(
        self,
        response: Response,
        request_id: str,
        path: str,
    ) -> Response:

        response.headers[
            "X-Request-ID"
        ] = request_id

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Referrer-Policy"
        ] = "no-referrer"

        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        response.headers[
            "X-Permitted-Cross-Domain-Policies"
        ] = "none"


        if path.startswith(
            "/api/v1/auth"
        ):

            response.headers[
                "Cache-Control"
            ] = (
                "no-store, "
                "max-age=0"
            )

            response.headers[
                "Pragma"
            ] = "no-cache"


        if (
            self.environment
            == "production"
        ):

            response.headers[
                "Strict-Transport-Security"
            ] = (
                "max-age=31536000; "
                "includeSubDomains"
            )


        return response


    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        request_id = str(
            uuid.uuid4()
        )

        path = (
            request.url.path
        )

        method = (
            request.method.upper()
        )


        # --------------------------
        # Readiness endpoint
        # --------------------------

        if (
            method == "GET"
            and path == "/ready"
        ):

            ready = (
                database_readiness()
            )

            status_code = (
                200
                if ready
                else 503
            )

            response = JSONResponse(
                status_code=status_code,
                content={
                    "status": (
                        "ready"
                        if ready
                        else "not_ready"
                    ),

                    "database": (
                        "ok"
                        if ready
                        else "unavailable"
                    ),
                },
            )

            return (
                self.add_security_headers(
                    response,
                    request_id,
                    path,
                )
            )


        # --------------------------
        # Request body boundary
        # --------------------------

        if not check_request_size(
            request
        ):

            response = JSONResponse(
                status_code=413,
                content={
                    "detail": (
                        "Request body "
                        "too large."
                    )
                },
            )

            return (
                self.add_security_headers(
                    response,
                    request_id,
                    path,
                )
            )


        # --------------------------
        # Pagination boundary
        # --------------------------

        if not check_pagination_limit(
            request
        ):

            response = JSONResponse(
                status_code=422,
                content={
                    "detail": (
                        "page_size cannot "
                        "exceed 100."
                    )
                },
            )

            return (
                self.add_security_headers(
                    response,
                    request_id,
                    path,
                )
            )


        # --------------------------
        # Sensitive auth rate limit
        # --------------------------

        limited, retry_after = (
            is_rate_limited(
                request
            )
        )


        if limited:

            response = JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many requests. "
                        "Please try again "
                        "shortly."
                    )
                },
            )

            if retry_after:

                response.headers[
                    "Retry-After"
                ] = str(
                    retry_after
                )


            return (
                self.add_security_headers(
                    response,
                    request_id,
                    path,
                )
            )


        started_at = (
            time.perf_counter()
        )


        try:

            response = await call_next(
                request
            )


        except Exception as exc:

            # Production logs avoid
            # request bodies, headers,
            # tokens and exception text.

            if (
                self.environment
                == "production"
            ):

                logger.error(
                    (
                        "Unhandled request "
                        "failure "
                        "request_id=%s "
                        "method=%s "
                        "path=%s "
                        "type=%s"
                    ),
                    request_id,
                    method,
                    path,
                    type(exc).__name__,
                )

            else:

                logger.exception(
                    (
                        "Unhandled request "
                        "failure "
                        "request_id=%s "
                        "method=%s "
                        "path=%s"
                    ),
                    request_id,
                    method,
                    path,
                )


            response = JSONResponse(
                status_code=500,
                content={
                    "detail": (
                        "Internal server "
                        "error."
                    ),

                    "request_id":
                        request_id,
                },
            )


        duration_ms = (
            time.perf_counter()
            - started_at
        ) * 1000


        logger.info(
            (
                "request_id=%s "
                "method=%s "
                "path=%s "
                "status=%s "
                "duration_ms=%.2f"
            ),
            request_id,
            method,
            path,
            response.status_code,
            duration_ms,
        )


        return (
            self.add_security_headers(
                response,
                request_id,
                path,
            )
        )