from app.core.security import (
    hash_password,
    verify_password,
)


def test_password_hashing():
    plain_password = "mypassword123"

    hashed_password = hash_password(
        plain_password
    )

    print("Plain password:")
    print(plain_password)

    print("\nHashed password:")
    print(hashed_password)

    if plain_password == hashed_password:
        print("\nERROR: Password was not hashed.")
    else:
        print("\nPassword hashing successful.")


def test_correct_password():
    plain_password = "mypassword123"

    hashed_password = hash_password(
        plain_password
    )

    result = verify_password(
        plain_password,
        hashed_password,
    )

    print(
        f"Correct password verification: {result}"
    )


def test_wrong_password():
    hashed_password = hash_password(
        "mypassword123"
    )

    result = verify_password(
        "wrongpassword",
        hashed_password,
    )

    print(
        f"Wrong password verification: {result}"
    )


if __name__ == "__main__":
    test_password_hashing()
    test_correct_password()
    test_wrong_password()