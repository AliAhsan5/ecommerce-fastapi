from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_valid_user():
    user = UserCreate(
        full_name="Ali Ahsan",
        email="ali@example.com",
        password="mypassword123",
    )

    print("Valid user:")
    print(user)


def test_invalid_user():
    try:
        UserCreate(
            full_name="A",
            email="not-an-email",
            password="123",
        )

    except ValidationError as error:
        print("\nValidation correctly failed:")
        print(error)


if __name__ == "__main__":
    test_valid_user()
    test_invalid_user()