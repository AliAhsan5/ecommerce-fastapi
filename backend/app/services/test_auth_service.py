from uuid import uuid4

from app.core.exceptions import AppException
from app.core.security import verify_password
from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.services.auth_service import register_user


def test_registration_service():
    db = SessionLocal()
    created_user = None

    test_email = (
        f"registration-test-{uuid4().hex[:8]}@example.com"
    )

    try:
        user_data = UserCreate(
            full_name="Test User",
            email=test_email,
            password="mypassword123",
        )

        created_user = register_user(
            db,
            user_data,
        )

        print("Registration successful:")
        print(
            created_user.id,
            created_user.full_name,
            created_user.email,
            created_user.role,
            created_user.is_active,
        )

        password_correct = verify_password(
            user_data.password,
            created_user.password_hash,
        )

        print(
            f"Password hashing verified: {password_correct}"
        )

        try:
            register_user(
                db,
                user_data,
            )

        except AppException as error:
            print(
                f"Duplicate email correctly rejected: "
                f"{error.status_code} - {error.message}"
            )

    finally:
        if created_user is not None:
            db.delete(created_user)
            db.commit()

            print("Temporary test user removed.")

        db.close()


if __name__ == "__main__":
    test_registration_service()