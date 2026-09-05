import jwt

from app.core.config import get_settings
from app.core.security import create_access_token


settings = get_settings()


def test_access_token():
    token = create_access_token(
        subject="123"
    )

    print("Access token:")
    print(token)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    print("\nDecoded payload:")
    print(payload)

    print(
        f"\nToken subject: {payload['sub']}"
    )


if __name__ == "__main__":
    test_access_token()