from sqlalchemy import text

from app.db.session import engine


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )

        return result.scalar_one()


if __name__ == "__main__":
    result = test_database_connection()
    print(f"Database connection successful: {result}")